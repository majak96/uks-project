from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [ 
    path('', views.index, name='index'),
    
    #projects
    path('project/', views.ProjectView.as_view(), name='all_projects'),
    path('project/new/', views.create_update_project, name='new_project'),
    path('project/<int:pk>/delete/', views.ProjectDelete.as_view(), name='delete_project'),
    path('project/<int:project_id>/edit/', views.create_update_project, name='edit_project'),
    path('project/<int:pk>/', views.OneProjectView.as_view(), name='one_project'),

    #issues
    path('project/<int:project_id>/issue/new/', views.create_update_issue, name='new_issue'),
    path('issue/<int:pk>/', views.OneIssueView.as_view(), name='one_issue'),
    path('project/<int:project_id>/issue/<int:pk>/delete/', views.IssueDelete.as_view(), name='delete_issue'),
    path('project/<int:project_id>/issue/<int:issue_id>/edit/', views.create_update_issue, name='edit_issue'),
    path('project/<int:project_id>/issue/<int:issue_id>/changestate/', views.change_issue_state, name='change_state_issue'),

    #comments
    path('issue/<int:issue_id>/comment/new/', views.create_update_comment, name='new_comment'),
    path('issue/<int:issue_id>/comment/<int:comment_id>/edit/', views.create_update_comment, name='edit_comment'),
    path('issue/<int:issue_id>/comment/<int:comment_id>/delete/', views.comment_delete_view, name='delete_comment'),
    path('comment/<int:pk>/', views.OneCommentView.as_view(), name='one_comment'),

    #milestone
    path('project/<int:project_id>/milestone/new/', views.create_update_milestone, name='new_milestone'),
    path('project/<int:project_id>/milestone/<int:pk>/', views.OneMilestoneView.as_view(), name='one_milestone'),
    path('project/<int:project_id>/milestone/<int:pk>/delete/', views.MilestoneDelete.as_view(), name='delete_milestone'),
    path('project/<int:project_id>/milestone/<int:milestone_id>/edit/', views.create_update_milestone, name='edit_milestone'),

    # issue milestone
    path('issue/<int:issue_id>/milestone/choose', views.choose_milestone, name='choose_milestone'),
    path('issue/<int:issue_id>/milestone/<int:milestone_id>/delete', views.remove_milestone, name='remove_milestone'),

    #labels
    path('issue/<int:issue_id>/label/new', views.create_label, name='new_label'),
    path('issue/<int:issue_id>/label/choose', views.choose_label, name='choose_label'),
    path('issue/<int:issue_id>/label/<int:label_id>/delete', views.remove_label, name='remove_label'),

    #search
    path('search/', views.search_projects, name='search'),

    #users
    path('register/', views.register_user, name="register"),
    path('logout/', auth_views.LogoutView.as_view(template_name = 'uks_app/logout.html'), name="logout"),
    path('login/', auth_views.LoginView.as_view(template_name = 'uks_app/login.html'), name="login"),
    path('profile/<str:id>/', views.profile, name="profile"),
    path('profile/<str:id>/update', views.profile_update, name="profile_update"),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name = 'uks_app/password_reset.html'), name="password_reset"),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name = 'uks_app/password_reset_done.html'), name="password_reset_done"),
    path('password-reset-confirm/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name = 'uks_app/password_reset_confirm.html'), name="password_reset_confirm"),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name = 'uks_app/password_reset_complete.html'), name="password_reset_complete"),

    #codeChange
    path('api/hello/', views.hook_receiver_view),

    path('api/chart/data/<int:project_id>', views.ChartData.as_view()),

    # followers 
    path('api/user/follow', views.follow),
    path('api/user/unfollow', views.unfollow),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

