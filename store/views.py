from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render,redirect

from django.urls import reverse,reverse_lazy

from django.views.generic import View,TemplateView,UpdateView,CreateView,DetailView,ListView,FormView

from store.forms import SignUpForm,LoginForm,UserprofileForm,ProjectForm,ReviewForm

from django.contrib.auth import authenticate,login

from store.models import UserProfile,Project,WishListItems,OrderSummary,Reviews

from decouple import config

class SignUpView(View):

    def get(self,request,*args,**kwargs):

        form_instance=SignUpForm()

        return render(request,"store/signup.html",{"form":form_instance})
    
    

    def post(self,request,*args,**kwargs):

        form_instance=SignUpForm(request.POST)

        if form_instance.is_valid():

            form_instance.save()

            return redirect("signin")
        
        else:

            return render(request,"store/signup.html",{"form":form_instance})
        


class SignInView(View):

    def get(self,request,*args,**kwargs):

        form_instance=LoginForm()

        return render(request,"store/login.html",{"form":form_instance})
    

    def post(self,request,*args,**kwargs):

        form_instance=LoginForm(request.POST)

        if form_instance.is_valid():

           data=form_instance.cleaned_data
           user_obj=authenticate(request,**data)


           if user_obj:
               
               login(request,user_obj)

               return redirect("index")
               
        else:
            
            return render(request,"store/login.html",{"form":form_instance})
        
KEY_SECRET=config('KEY_SECRET')

KEY_ID=config('KEY_ID')


class IndexView(View):

    template_name="store/index.html"

    def get(self,request,*args,**kwargs):

        qs=Project.objects.all().exclude(owner=request.user)

        return render(request,self.template_name,{"projects":qs})
    






class UserProfileUpdateView(UpdateView):


    model=UserProfile

    form_class=UserprofileForm

    template_name="store/profile_edit.html"

#   def get_success_url(self):
#     return reverse("index")
#or
    success_url=reverse_lazy("index") 
                            
                            


#    def get(self,request,*args,**kwargs):


#        id=kwargs.get("pk")

#        profile_obj=UserProfile.objects.get(id=id)

#       form_instance=UserprofileForm(instance=profile_obj)

#       return render(request,"store/profile_edit.html",{"form":form_instance})



class ProjectCreateView(CreateView):

    model=Project

    form_class=ProjectForm

    template_name="store/project_add.html"

    success_url=reverse_lazy("index")

    def form_valid(self,form):

        form.instance.owner=self.request.user
        return super().form_valid(form)
    


class ProjectListView(View):

    def get(self,request,*args,**kwargs):

        #qs=Project.objects.filter(owner=request.user)

        qs=request.user.projects.all()

        return render(request,"store/myprojects.html",{"works":qs})
    

class ProjectDeleteView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        Project.objects.get(id=id).delete()

        return redirect("myworks")
    


class ProjectDetailView(DetailView):

    template_name="store/project_detail.html"

    context_object_name="project"

    model=Project


class AddToWishListView(View):

    def get(self,request,*args,**kwargs):

        id= kwargs.get("pk")

        project_obj=Project.objects.get(id=id)

        WishListItems.objects.create(
                                        wishlist_object=request.user.basket,
                                        project_object=project_obj
        )
        print("item has been added to wishlist")


        return redirect("index")
    

from django.db.models import Sum

class MyCartView(View):

    def get(self,request,*args,**kwargs):

        qs=request.user.basket.basket_items.filter(is_order_placed=False)

        total=request.user.basket.wishlist_total


        return render(request,"store/wishlist_summary.html",{"cartitems":qs,"total":total})
    



class WishListItemDeleteView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        WishListItems.objects.get(id=id).delete()

        return redirect("my-cart")
    
import razorpay

class CheckOutView(View):
    def get(self,request,*args,**kwargs):

        
        client = razorpay.Client(auth=(KEY_ID,KEY_SECRET))

        amount=request.user.basket.wishlist_total*100

        data = { "amount": amount, "currency": "INR", "receipt": "order_rcptid_11" }
        payment = client.order.create(data=data)

        #create order object
        
        cart_items=request.user.basket.basket_items.filter(is_order_placed=False)

        order_summary_obj=OrderSummary.objects.create(
            user_object=request.user,
            order_id=payment.get("id"),
            total=request.user.basket.wishlist_total



        )
       # order_summary_obj.project_object.add(cart_items.values("project_object"))

        for ci in cart_items:

           order_summary_obj.project_object.add(ci.project_object)

           order_summary_obj.save()

        
        # for ci in cart_items:
        #     ci.is_order_placed=True
        #     ci.save()


       
    
        

        context={
                "key":KEY_ID,
                "amount":data.get("amount"),
                "currency":data.get("currency"),
                "order_id":payment.get("id")
        }

        return render(request,"store/payment.html",context)

from django.views.decorators.csrf import csrf_exempt

from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt,name="dispatch")
class PaymentVerificationView(View):

    def post(self,request,*args,**kwargs):

        print(request.POST)
        
        client = razorpay.Client(auth=(KEY_ID,KEY_SECRET))
        order_summary_object=OrderSummary.objects.get(order_id=request.POST.get("razorpay_order_id"))
        login(request,order_summary_object.user_object)
        try:
            #doubtfulcode
            client.utility.verify_payment_signature(request.POST)
            print("payment success")
            order_id=request.POST.get("razorpay_order_id")
            OrderSummary.objects.filter(order_id=order_id).update(is_paid=True)
            cart_items=request.user.basket.basket_items.filter(is_order_placed=False)

            for ci in cart_items:
                print("text",ci)
                ci.is_order_placed=True
                ci.save()

        except:

            #handlingcode
             print("payment fail")



       # return render(request,"store/success.html")
        return redirect('index')
    

class MyPurchaseView(View):
    model=OrderSummary

    context_object_name="orders"

    def get(self,request,*args,**kwargs):

        qs=OrderSummary.objects.filter(user_object=request.user,is_paid=True).order_by('created_date')

        return render(request,"store/order_summary.html",{"orders":qs})
    

class ReviewCreateView(FormView):
#url locailhost:8000/project/<int:pk>/review/add/
    template_name="store/review.html"

    form_class=ReviewForm

    def post(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        project_obj=Project.objects.get(id=id)
        

        form_instance=ReviewForm(request.POST)

        if form_instance.is_valid:

            form_instance.instance.user_object=request.user

            form_instance.instance.project_objects=project_obj

            form_instance.save()

            return redirect('index')
        else:
            return render(request,self.template_name,{"form":form_instance})
        

   




    

        
       



                                 








    


         







   
    



    



    

