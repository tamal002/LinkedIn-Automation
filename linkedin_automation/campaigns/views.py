# campaigns/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import LinkedinLoginForm
from .tasks import run_linkedin_login_and_search, send_linkedin_invites
from django.urls import reverse




def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to Django's built-in login page
    else:
        form = UserCreationForm()
    
    return render(request, 'campaigns/register.html', {'form': form})





@login_required
def domain_input(request):
    if request.method == 'POST':
        form = LinkedinLoginForm(request.POST)
        if form.is_valid():
            linkedin_email = form.cleaned_data['linkedin_email']
            linkedin_password = form.cleaned_data['linkedin_password']
            domain = form.cleaned_data['domain']

            # Run Playwright task
            raw_profiles = run_linkedin_login_and_search(
                linkedin_email,
                linkedin_password,
                domain
            )

            # Wrap each URL in a dict for template rendering
            profiles = [{'url': url} for url in raw_profiles]

            # Save to session temporarily (for next step)
            request.session['linkedin_email'] = linkedin_email
            request.session['linkedin_password'] = linkedin_password
            request.session['domain'] = domain
            request.session['profiles'] = profiles  # list of profile dicts

            return render(request, 'campaigns/results.html', {
                'profiles': profiles,
                'domain': domain
            })
    else:
        initial_data = {
            'linkedin_email': request.session.get('linkedin_email', ''),
            'domain': request.session.get('domain', '')
        }
        form = LinkedinLoginForm(initial=initial_data)

    return render(request, 'campaigns/search_form.html', {'form': form})





@login_required
def results_page(request):
    return redirect('campaigns:domain_input')




@login_required
def run_automation(request):
    # Get data from session
    linkedin_email = request.session.get('linkedin_email')
    linkedin_password = request.session.get('linkedin_password')
    domain = request.session.get('domain')
    profiles = request.session.get('profiles', [])

    if not linkedin_email or not linkedin_password or not domain:
        return redirect('campaigns:domain_input')

    if request.method == 'POST':
        # Trigger automation logic
        sent_profiles = send_linkedin_invites(linkedin_email, linkedin_password, profiles, domain=domain)

        return render(request, 'campaigns/success.html', {
            'sent_profiles': sent_profiles,
            'total_sent': len([p for p in sent_profiles if p['status'] == 'Sent'])
        })

    # GET request - show confirmation
    return render(request, 'campaigns/confirm_send.html', {
        'profiles': profiles
    })