from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms

from . import util
import random
import markdown2




class NewEntryForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control", 
                                                          "placeholder":"Title"}))
    text = forms.CharField(widget=forms.Textarea(attrs={'class': "form-control", 
                                                        "placeholder":"Content of the entry"}))

class EditForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'class': "form-control"}))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    entry = util.get_entry(title)
    if  entry is not None:
        return render(request, "encyclopedia/entry.html",
            {"title" : title , "entry" : markdown2.markdown(entry)})

    return render(request, "encyclopedia/error.html", 
                {"title": title})

def search(request):
    if request.GET.get('title') is None:
        title = random.choice(util.list_entries())
        return HttpResponseRedirect(reverse("encyclopedia:title", kwargs={"title" : title}))

    else:
        title = request.GET.get('title')
        titles = util.list_entries()
        if title in titles:
            return HttpResponseRedirect(reverse("encyclopedia:title", kwargs={'title': title}))
        else:
            matches = [match for match in titles if title.lower() in match.lower()]
            return render(request, "encyclopedia/search_results.html",{"results": matches})
        
def create(request):
    if request.method == "POST":    
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title'] 
            if title not in util.list_entries():
                util.save_entry(title, form.cleaned_data['text'])
                return HttpResponseRedirect(reverse("encyclopedia:title", kwargs = {'title' : title}))
            else:
                form = NewEntryForm()
                return render(request,"encyclopedia/create.html",{"form":form, "message": True})
    
    else :
        form = NewEntryForm()
        return render(request,"encyclopedia/create.html",
                      {"form":form, "message": False})
    
def edit(request,title):
    if request.method == "POST":
        form = EditForm(request.POST)
        if form.is_valid():
            util.save_entry(title, form.cleaned_data['text'])
            return HttpResponseRedirect(reverse("encyclopedia:title", kwargs = {'title' : title}))
    
    request.session['title'] = title
    form = EditForm({"text": util.get_entry(title)})
    return render(request, "encyclopedia/edit.html", context = {"form":form})


