from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.views import generic
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView

from .models import ObservedProject, Issue, Milestone, MilestoneChange, Event, Label, User, Comment, CommentChange
from .forms import ProjectForm, IssueForm, MilestoneForm, LabelForm, ChooseLabelForm, UserRegisterForm, UserUpdateForm, ProfileUpdateForm, ChooseMilestoneForm, CommentForm
import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import datetime

# home page
def index(request): 
    return render(request, 'uks_app/index.html') #optional third argument context

# new project form
@login_required
def create_update_project(request, project_id=None):
 
    user = request.user

    #project_id == None -> Create
    #project_id != None -> Update
    observed_project = get_object_or_404(ObservedProject, pk=project_id) if project_id else None

    form = ProjectForm(request.POST or None, instance=observed_project)

    if form.is_valid():
         
        project = form.save(commit=False) 
 
        project.user = user
        project.save()

        if project_id:
            return HttpResponseRedirect('/project/' + str(project_id) + '/')  
        else:
            return HttpResponseRedirect('/project/')

    context = {
        'form' : form,
    }

    return render(request, 'uks_app/create_update_project.html', context)

# new issue form
def create_update_issue(request, project_id, issue_id=None):

    #get observed project
    observed_project = get_object_or_404(ObservedProject, id=project_id)

    #issue_id == None -> Create
    #issue_id != None -> Update
    observed_issue = get_object_or_404(Issue, pk=issue_id) if issue_id else None

    form = IssueForm(request.POST or None, instance=observed_issue)

    if form.is_valid():
        issue = form.save(commit=False)
        
        #set project as foreign key
        issue.project = observed_project
        issue.save()
        
        if issue_id:
            return HttpResponseRedirect('/issue/' + str(issue_id) + '/')  
        else:
            return HttpResponseRedirect('/issue/' + str(issue.id) + '/')  

    cancel_url = "../../../../../issue/"+str(issue_id) if issue_id else "../../"

    
    context = {
        'form' : form,
        'cancel_url': cancel_url
    }

    return render(request, 'uks_app/create_update_issue.html', context)

# new label form
@login_required
def create_label(request, issue_id):

    #get issue
    observed_issue = get_object_or_404(Issue, pk=issue_id)

    form = LabelForm(request.POST or None)

    if form.is_valid():
        label = form.save(commit=True)
        
        #set issue as foreign key
        label.issue.add(observed_issue)
        label.save()
        
        return HttpResponseRedirect('/issue/' + str(issue_id) + '/')

    context = {
        'form' : form,
    }

    return render(request, 'uks_app/create_label.html', context)

# choose label
@login_required
def choose_label(request, issue_id):

    #get issue and project
    observed_issue = get_object_or_404(Issue, pk=issue_id)
    observed_project = observed_issue.project

    project_issues = observed_project.issue_set.exclude(id=issue_id)

    form = ChooseLabelForm(project_issues, observed_issue, data=request.POST or None)

    if form.is_valid():
    
        chosen_labels = form.cleaned_data['labels']
        
        for label in chosen_labels:
            label.issue.add(observed_issue)
            label.save()
        
        return HttpResponseRedirect('/issue/' + str(issue_id) + '/')

    context = {
        'form' : form,
        'issue' : observed_issue
    }

    return render(request, 'uks_app/choose_label.html', context)


#change issue state
def change_issue_state(request, project_id, issue_id):

    #get observed project
    observed_project = get_object_or_404(ObservedProject, id=project_id)
    
    #get issue
    observed_issue = get_object_or_404(Issue, id=issue_id)

    if observed_issue.state == "OP":
        observed_issue.state = "CL"
    else:
        observed_issue.state = "OP"
    
    observed_issue.save()

    return HttpResponseRedirect('/issue/' + str(issue_id) + '/')

@login_required
def remove_label(request, label_id, issue_id):

    #get issue
    issue = get_object_or_404(Issue, id=issue_id)

    #get label
    label = get_object_or_404(Label, id=label_id)

    issue.labels.remove(label)

    if label.issue.count() <= 0:
        label.delete()

    return HttpResponseRedirect('/issue/' + str(issue_id) + '/')

#search projects from name
def search_projects(request):
    search_name = request.GET['search']
    observed_projects = ObservedProject.objects.filter(name__icontains=search_name.lower()).filter(public = 'True')
    issues_list =Issue.objects.filter(title__icontains=search_name.lower(), project__public='True')
    users_list=User.objects.filter(Q(first_name__icontains = search_name.lower()) | Q(last_name__icontains = search_name.lower()) | Q(username__icontains = search_name.lower()) & Q(is_staff='False'))
    return render(request, 'uks_app/search_result.html', {'observed_projects': observed_projects, 'issues_list':issues_list, 'users_list':users_list})

# user registration 
def register_user(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Your account has been created! You are able to log in now!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, "uks_app/register.html", {'form' : form})

# user profile
def profile(request, id=None):
    selected_user = get_object_or_404(User, username=id)
    projects = ObservedProject.objects.filter(user=selected_user)
    update_possible = selected_user == request.user
    print(update_possible)
    context = {"selected_user": selected_user, 'projects' : projects, 'update_possible' : update_possible}
    return render(request, 'uks_app/profile.html', context)

# user profile update
@login_required
def profile_update(request, id=None):
    selected_user = get_object_or_404(User, username=id)

    if request.user != selected_user:
        return HttpResponse('Unauthorized', status=401)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=selected_user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=selected_user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile', selected_user.username)
    else:
        u_form = UserUpdateForm(instance=selected_user)
        p_form = ProfileUpdateForm(instance=selected_user.profile)

    context = {
        'u_form' : u_form,
        'p_form' : p_form
    }
    return render(request, 'uks_app/profile_update.html', context)

#delete project
class ProjectDelete(DeleteView):
    template_name = 'uks_app/delete_project.html'
    model = ObservedProject

    success_url = reverse_lazy('all_projects')

#delete issue
class IssueDelete(DeleteView):
    template_name = 'uks_app/delete_issue.html'
    model = Issue

    def get_success_url(self):
        project = self.object.project
        return reverse_lazy( 'one_project', kwargs={'pk': project.id})

# all projects view
class ProjectView(generic.ListView):
    template_name = 'uks_app/all_projects.html'
    context_object_name = 'project_list'

    def get_queryset(self):
        return ObservedProject.objects.all()

# one project detailed view
class OneProjectView(generic.DetailView):
    model = ObservedProject
    template_name = 'uks_app/one_project.html'

# one issue detailed view
class OneIssueView(generic.DetailView):
    model = Issue
    template_name = 'uks_app/one_issue.html'

    def get_context_data(self, **kwargs):
        context = super(OneIssueView, self).get_context_data(**kwargs)
        context['events'] = Event.objects.filter(issue_id=self.kwargs.get('pk')).order_by('time')

        return context

# one milestone detailed view
class OneMilestoneView(generic.DetailView):
    model = Milestone
    template_name = 'uks_app/one_milestone.html'

#delete milestone
class MilestoneDelete(DeleteView):
    template_name = 'uks_app/delete_issue.html'
    model = Milestone

    success_url = reverse_lazy('all_projects')

# new milestone
def create_update_milestone(request, project_id, milestone_id=None):

    #get observed project
    observed_project = get_object_or_404(ObservedProject, id=project_id)

    #milestone_id == None -> Create
    #milestone_id != None -> Update
    observed_milestone = get_object_or_404(Milestone, pk=milestone_id) if milestone_id else None

    form = MilestoneForm(request.POST or None, instance=observed_milestone)

    if form.is_valid():
        milestone = form.save(commit=False)
        
        #set project as foreign key
        milestone.project = observed_project
        milestone.save()
        
        if milestone_id:
            return HttpResponseRedirect('/project/' + str(project_id) + '/milestone/' + str(milestone_id) + '/')  
        else:
            return HttpResponseRedirect('/project/' + str(project_id) + '/milestone/' + str(milestone.id) + '/')  

    context = {
        'form' : form,
    }
    return render(request, 'uks_app/create_update_milestone.html', context)
    
# choose label
@login_required
def choose_milestone(request, issue_id):

    
    #get issue and project
    observed_issue = get_object_or_404(Issue, pk=issue_id)
    observed_project = observed_issue.project

    form = ChooseMilestoneForm(observed_project, observed_issue, data=request.POST or None)

    user = request.user

    if form.is_valid():
    
        chosen_milestones = form.cleaned_data['milestones']
        
        for milestone in chosen_milestones:
            milestone_change = MilestoneChange.objects.create(time = datetime.datetime.now(), user = user, issue = observed_issue, checkpoint=milestone, add=True) 
            milestone_change.save()
            #observed_issue.milestonechanges.add(milestone_change)
            #observed_issue.save()

            milestone.issue.add(observed_issue)
            milestone.save()
        
        return HttpResponseRedirect('/issue/' + str(issue_id) + '/')

    context = { 
         'form' : form,
         'issue' : observed_issue
    }

    return render(request, 'uks_app/choose_milestone.html', context)

@login_required
def remove_milestone(request, milestone_id, issue_id):

    #get issue
    issue = get_object_or_404(Issue, id=issue_id)

    #get milestone
    milestone = get_object_or_404(Milestone, id=milestone_id)

    issue.milestones.remove(milestone)

    user = request.user
    milestone_change = MilestoneChange.objects.create(time = datetime.datetime.now(), user = user, issue = issue, checkpoint=milestone, add=False) 

    return HttpResponseRedirect('/issue/' + str(issue_id) + '/') 

# new comment form
@login_required
def create_update_comment(request, issue_id, comment_id=None):
    #get issue
    observed_issue = get_object_or_404(Issue, id=issue_id)
    #comment_id == None -> Create
    #comment_id != None -> Update
    observed_comment = get_object_or_404(Comment, pk=comment_id) if comment_id else None

    initial = ''

    if observed_comment:
        initial = observed_comment.description

        comment_changes = observed_comment.commentchange_set.all()
        print(comment_changes)

        if comment_changes:
            initial = comment_changes.reverse()[0]

    form = CommentForm(request.POST or None, instance=observed_comment, initial={'description': initial})
    #form.fields["description"].initial = 'initialllll'

    user = request.user

    if form.is_valid():

        if comment_id:
            if (user == observed_comment.user):
                comment = form.save(commit=False)
                commentChange = CommentChange(comment = comment, newComment=comment.description, time = datetime.datetime.now())
                commentChange.save()
            else:
                return HttpResponse('Unauthorized', status=401)
        else:
            comment = form.save(commit=False)            
            #set issue as foreign key
            comment.issue = observed_issue
            comment.time = datetime.datetime.now()
            comment.user = user
            comment.save()
        
        return HttpResponseRedirect('/issue/' + str(issue_id) + '/')  

    cancel_url = "../../../../../issue/"+str(issue_id) if issue_id else "../../"

    context = {
        'form' : form,
        'cancel_url': cancel_url
    }
    return render(request, 'uks_app/create_update_comment.html', context)

# delete comment
@login_required
def comment_delete_view(request, issue_id, comment_id):
    observed_issue = get_object_or_404(Issue, id=issue_id)  #get issue
    user = request.user
    observed_comment = get_object_or_404(Comment, id=comment_id)
    if (user == observed_comment.user):           
        observed_comment.delete()
    else:
        return HttpResponse('Unauthorized', status=401)
    return HttpResponseRedirect('/issue/' + str(issue_id) + '/') 

# one comment detailed view
class OneCommentView(generic.DetailView):
    model = Comment
    template_name = 'uks_app/one_comment.html'

    
