import cgi
from datetime import datetime

import boto3
from django import template
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.template import loader
from django.views import generic

from django.shortcuts import render, redirect
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Task, ResolutionStatus
from .forms import TaskForm, ReportForm
from django.core.files.storage import default_storage
from allauth.socialaccount.models import SocialApp

from honor.models import Report


# Create your views here.
# class IndexView(generic.ListView):
# template_name = "honor/index.html"
# def get_queryset(self):
#     return
def index(request):
    template = loader.get_template("honor/index.html")
    # context = {"title":"honor"}
    return render(request, "honor/index.html")


def report(request):
    template = loader.get_template("honor/report.html")
    return render(request, "honor/report.html")


def submit_report(request):
    if not request.session.session_key:
        request.session.create()
    print(request.session.session_key)
    # getting the information inputted into the report fields #
    nameOfOffender = request.POST.get("nameOfOffender")
    className = request.POST.get("className")
    location = request.POST.get("location")
    description = request.POST.get("description")
    addInfo = request.POST.get("addInfo")
    file = request.FILES.get("file")
    file_key = None
    #admin_comments = request.POST.get("admin_comments")

    timeStamp = datetime.now()

    print(nameOfOffender, className, location, description, addInfo)
    if not nameOfOffender and not className and not location and not description and not addInfo and not file:
        # if user didn't input any information into the fields
        return render(request, "honor/report.html", {"error_message": "Please fill out atleast one field"})
        # return HttpResponseRedirect(reverse("polls:submitted", args=(question_id,title)))
    else:
        if request.user.is_authenticated:
            filedReport = Report.objects.create(user=request.user, nameOfOffender=nameOfOffender, className=className, location=location, description=description, addInfo=addInfo, file=file)
        else:
            filedReport = Report.objects.create(session_id=request.session.session_key, nameOfOffender=nameOfOffender, className=className, location=location, description=description, addInfo=addInfo,)


        return render(request, "honor/index.html")
def edit_report(request):
    # getting the information inputted into the report fields #
    reportId = request.POST.get("Id")
    nameOfOffender = request.POST.get("nameOfOffender")
    className = request.POST.get("className")
    location = request.POST.get("location")
    description = request.POST.get("description")
    addInfo = request.POST.get("addInfo")
    existing_report = Report.objects.get(id=reportId)  # Replace `report_id` with the actual ID of the report you want to edit

    timeStamp = datetime.now()
    files = request.FILES.getlist("file")

    print(nameOfOffender, className, location, description, addInfo)
    if not nameOfOffender and not className and not location and not description and not addInfo:
        # if user didn't input any information into the fields
        return render(request, "honor/reportEdit.html", {"report": existing_report, "error_message": "Please fill out atleast one field"})
        # return HttpResponseRedirect(reverse("honor:reportEdit", args=(reportId,)))
    else:
        existing_report.nameOfOffender = nameOfOffender
        existing_report.className = className
        existing_report.location = location
        existing_report.description = description
        existing_report.addInfo = addInfo
        existing_report.status = ResolutionStatus.NEW
        existing_report.save()
        # filedReport = Report.objects.create(nameOfOffender=nameOfOffender, className=className, location=location, description=description, addInfo=addInfo)

        # for file in files:
        #     reportFile = File.objects.create(report=filedReport, file=file)

        # return render(request, "honor/"+reportId+"/reportDisplay.html")
        return HttpResponseRedirect(reverse("honor:reportDisplay", args=(reportId,)))

import boto3
from .forms import ReportForm

#Citation: https://www.hacksoft.io/blog/direct-to-s3-file-upload-with-django
def submitted_view(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            attachment_file = request.FILES.get('attachment') 
            if attachment_file:
                s3 = boto3.client('s3')
                bucket_name = 'honor-bucket-v2'
                s3.upload_fileobj(attachment_file, bucket_name)
            report = Report(
                nameOfOffender=form.cleaned_data['nameOfOffender'],
                description=form.cleaned_data['description'],
            )
            report.save()

            return redirect('success_page')
    else:
        form = ReportForm()
    
    if request.user.groups.filter(name="power-user").exists():
        report_list = Report.objects.all()
    elif request.user.is_authenticated:
        report_list = Report.objects.filter(user=request.user)
    else:
        report_list = Report.objects.filter(session_id=request.session.session_key)

    context = {
        'report_list': report_list,
        'form': form,
    }
    return render(request, 'honor/submitted.html', context)


def reportDisplay_view(request, report_id): #,report_number
    # Retrieve report list
    report = Report.objects.get(id=report_id)

    if request.user.groups.filter(name="power-user").exists() and report.status == ResolutionStatus.NEW:
        print("updating status")
        report.status = ResolutionStatus.IN_PROGRESS
        report.save()

    context = {
        'report': report,
        'report_status': report.get_status(),
        #'report_number': report_number
    }
    return render(request, 'honor/reportDisplay.html', context)
def reportEdit_view(request, report_id):
    # Retrieve report list
    report = Report.objects.get(id=report_id)

    context = {
        'report': report,
        'report_status': report.get_status()
    }
    return render(request, 'honor/reportEdit.html', context)

#Citation: https://www.youtube.com/watch?v=yO6PP0vEOMc
def login(request):
    template = loader.get_template("honor/login.html")
    return render(request, "honor/login.html")

#Citation: https://www.youtube.com/watch?v=yO6PP0vEOMc
def logout_view(request):
    #if request.user.is_authenticated:
    logout(request)
    return redirect("/")

# THIS METHOD IS FOR TESTING
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            # Process the form data if needed
            form.save()
            # Clear the form for a new task
            form = TaskForm()
    else:
        form = TaskForm()

    return render(request, 'honor/create_task.html', {'form': form})


# THIS METHOD IS FOR TESTING
def socialapp_check(request):
    try:
        google_app = SocialApp.objects.get(provider='google')
        context = {'google_app_exists': True}
    except SocialApp.DoesNotExist:
        context = {'google_app_exists': False}

    return render(request, 'honor/socialapp_check.html', context)

def add_admin_comments(request, report_id):
    report = Report.objects.get(id=report_id)
    report.admin_comments = request.POST.get('comments', '')
    # report.status = ResolutionStatus.RESOLVED
    report.save()

    #TODO: this is a placeholder, redirect to a confirmation page or whatever
    context = {
        'report': report,
        'report_status': report.get_status()
    }
    return render(request, 'honor/reportDisplay.html', context)

def resolve(request, report_id):
    report = Report.objects.get(id=report_id)
    report.status = ResolutionStatus.RESOLVED
    report.save()

    #TODO: this is a placeholder, redirect to a confirmation page or whatever
    context = {
        'report': report,
        'report_status': report.get_status()
    }
    return render(request, 'honor/reportDisplay.html', context)

def delete_report(request, report_id):
    report = Report.objects.get(id=report_id)
    report.delete()

    if request.user.groups.filter(name="power-user").exists():
        report_list = Report.objects.all()
    elif request.user.is_authenticated:
        report_list = Report.objects.filter(user=request.user)
    else:
        report_list = Report.objects.filter(session_id=request.session.session_key)

    context = {
        'report_list': report_list,
    }
    return render(request, 'honor/submitted.html', context)


def continue_anonymously(request):
    logout(request)
    return render(request, 'honor/index.html')