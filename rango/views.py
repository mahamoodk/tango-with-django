from django.shortcuts import render
from django.http import HttpResponse
from . models import Category, Page
from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

def index(request):
	request.session.set_test_cookie()
# Query the database for a list of ALL categories currently stored.
# Order the categories by no. likes in descending order.
# Retrieve the top 5 only - or all if less than 5.
# Place the list in our context_dict dictionary
# that will be passed to the template engine.
	category_list = Category.objects.order_by('-likes')[:5]
	page_list = Page.objects.order_by('-views')[:5]
	context = {'categories': category_list, 'pages':page_list}
# Render the response and send it back!
	return render(request, 'rango/index.html', context)
def about(request):
	if request.session.test_cookie_worked():
		print("TEST COOKIE WORKED!")
		request.session.delete_test_cookie()
# prints out whether the method is a GET or a POST
	print(request.method)
# prints out the user name, if no one is logged in it prints `AnonymousUser`
	print(request.user)
	return render(request, 'rango/about.html', {})
def get_category_list():
	return {'cats': Category.objects.all(), 'act_cat':cat}
def show_category(request, category_name_slug):
	context_dict = {}
	
	try:
		category = Category.objects.get(slug=category_name_slug)
		pages = Page.objects.filter(category=category)

		context_dict['pages'] = pages
		context_dict['category'] = category
	except Category.DoesNotExist:
		context_dict['category'] = None
		context_dict['pages'] = None

	return render (request, 'rango/category.html', context_dict)

def add_category(request):
	form = CategoryForm()
	# A HTTP POST?
	if request.method == 'POST':
		form = CategoryForm(request.POST)
		# Have we been provided with a valid form?
		if form.is_valid():
			# Save the new category to the database.
			form.save(commit=True)
			# Now that the category is saved
			# We could give a confirmation message
			# But since the most recent category added is on the index page
			# Then we can direct the user back to the index page.
			return index(request)
		else:
			print(form.errors)
			# The supplied form contained errors -
			# just print them to the terminal.
	return render(request, 'rango/add_category.html', {'form': form})	

def add_page(request, category_name_slug):
	try:
		category = Category.objects.get(slug=category_name_slug)
	except Category.doesNotExist:
		category = None

	form = PageForm()
	if request.method == 'POST' :
		form = PageForm(request.POST)
		if form.is_valid():
			if category:
				page = form.save(commit=False)
				page.category = category
				page.views = 0
				page.save()
				return show_category(request, category_name_slug)
		else:
			print(form.errors)
	
	context_dict = {'form':form, 'category': category}
	return render(request, 'rango/add_page.html',context_dict)
	
def register(request):
# A boolean value for telling the template
# whether the registration was successful.
# Set to False initially. Code changes value to
# True when registration succeeds.
	registered = False

	# If it's a HTTP POST, we're interested in processing form data.
	if request.method == 'POST':
# Attempt to grab information from the raw form information.
# Note that we make use of both UserForm and UserProfileForm.
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)
# If the two forms are valid...
		if user_form.is_valid() and profile_form.is_valid():
			# Save the user's form data to the database.
			user = user_form.save()
			# Now we hash the password with the set_password method.
			# Once hashed, we can update the user object.
			user.set_password(user.password)
			user.save()
			# Now sort out the UserProfile instance.
			# Since we need to set the user attribute ourselves,
			# we set commit=False. This delays saving the model
			# until we're ready to avoid integrity problems.
			profile = profile_form.save(commit=False)
			profile.user = user
			# Did the user provide a profile picture?
			# If so, we need to get it from the input form and
			#put it in the UserProfile model.
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']
			# Now we save the UserProfile model instance.
			profile.save()
			# Update our variable to indicate that the template
			# registration was successful.
			registered = True
		else:
		# Invalid form or forms - mistakes or something else?
		# Print problems to the terminal.
			print(user_form.errors, profile_form.errors)
	else:
		# Not a HTTP POST, so we render our form using two ModelForm instances.
		# These forms will be blank, ready for user inpu
		user_form = UserForm()
		profile_form = UserProfileForm()
# Render the template depending on the context.
	return render(request,
	'rango/register.html',
	{'user_form': user_form,
	'profile_form': profile_form,
	'registered': registered})

def user_login(request):
	if request.method == 'POST' :
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username=username, password=password)

		if user:
# Is the account active? It could have been disabled.
			if user.is_active:
# If the account is valid and active, we can log the user in.
# We'll send the user back to the homepage.
				login(request, user)
				return HttpResponseRedirect(reverse('index'))
			else:
# An inactive account was used - no logging in!
				return HttpResponse("Your Rango account is disabled.")
		else:
# Bad login details were provided. So we can't log the user in.
			#print("Invalid login details: {0}, {1}".format(username, password))
			return HttpResponse("Invalid login details:username- {0},password- {1}".format(username, password))#Invalid login details supplied
	
	else:
		return render(request, 'rango/login.html', {})								
						
@login_required
def restricted(request):
	return render(request, 'rango/restricted.html')

@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect(reverse('index'))
	
