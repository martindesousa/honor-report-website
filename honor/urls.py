from django.urls import path

from . import views

app_name = "honor"
urlpatterns = [
    #path("", views.IndexView.as_view(), name="index"),
    path("", views.login, name="login"),
    path("home/", views.index, name="index"),
    path("report/", views.report, name="report"),
    path("submit_report/", views.submit_report, name="submit_report"),
    path("edit_report/", views.edit_report, name="edit_report"),
    path("submitted/", views.submitted_view, name="submitted"),
    path("<int:report_id>/reportDisplay/", views.reportDisplay_view, name="reportDisplay"),
    path("<int:report_id>/reportEdit/", views.reportEdit_view, name="reportEdit"),
    path("logout_view/", views.logout_view, name = "logout_view"),
    path('create_task/', views.create_task, name='create_task'),
    path('socialapp_check', views.socialapp_check, name='socialapp_check'),
    path("<int:report_id>/add_admin_comments", views.add_admin_comments, name = "add_admin_comments"),
    path("<int:report_id>/resolve", views.resolve, name = "resolve"),
    path("<int:report_id>/delete_report", views.delete_report, name = "delete_report"),
    path("continue_anonymously/", views.continue_anonymously, name = "continue_anonymously")
]