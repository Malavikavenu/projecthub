from django.db import models

from django.contrib.auth.models import User

from embed_video.fields import EmbedVideoField

from django.db.models import Sum,Avg

#request.user
#UserProfile.objects.get(user_object=request.user)
#User->userprofile
#request.user.profile



class UserProfile(models.Model):

    bio=models.CharField(max_length=260,null=True)
    pic=models.ImageField(upload_to="profile_pic",default="/profile_pic/default.png")

    user_object=models.OneToOneField(User,on_delete=models.CASCADE,related_name="profile")

    created_date=models.DateTimeField(auto_now_add=True)

    updated_date=models.DateTimeField(auto_now=True)

    is_active=models.BooleanField(default=True)

    def __str__(self):

        return self.user_object.username
    



    
class Tag(models.Model):
    
    title=models.CharField(max_length=100,unique=True)

    created_date=models.DateTimeField(auto_now_add=True)

    updated_date=models.DateTimeField(auto_now=True)

    is_active=models.BooleanField(default=True)

    def __str__(self):

        return self.title
    


    
class Project(models.Model):

    title=models.CharField(max_length=100)

    description=models.TextField()

    tag_objects=models.ManyToManyField(Tag)

    owner=models.ForeignKey(User,on_delete=models.CASCADE,related_name="projects")

    thumbnail=EmbedVideoField()

    price=models.PositiveIntegerField()

    files=models.FileField(upload_to="projects",null=True)

    created_date=models.DateTimeField(auto_now_add=True)

    updated_date=models.DateTimeField(auto_now=True)

    is_active=models.BooleanField(default=True)

    @property
    def downloads(self):
        
       return OrderSummary.objects.filter(is_paid=True,project_object=self).count()
    
    @property
    def review_count(self):
        return self.project_reviews.all().count()
    
    @property
    def average_rating(self):
        return self.project_reviews.all().values('rating').aggregate(avg=Avg('rating')).get('avg',0)

    def __str__(self):

        return self.title
    


    
class WishList(models.Model):

    owner=models.OneToOneField(User,on_delete=models.CASCADE,related_name="basket")

    created_date=models.DateTimeField(auto_now_add=True)

    updated_date=models.DateTimeField(auto_now=True)

    is_active=models.BooleanField(default=True)

    @property
    def wishlist_total(self):
                
        return self.basket_items.filter(is_order_placed=False).values("project_object__price").aggregate(total=Sum("project_object__price")).get("total")

    



class WishListItems(models.Model):

    wishlist_object=models.ForeignKey(WishList,on_delete=models.CASCADE,related_name="basket_items")

    project_object=models.ForeignKey(Project,on_delete=models.CASCADE)

    is_order_placed=models.BooleanField(default=False)

    created_date=models.DateTimeField(auto_now_add=True)

    updated_date=models.DateTimeField(auto_now=True)

    is_active=models.BooleanField(default=True)



class OrderSummary(models.Model):

    user_object=models.ForeignKey(User,on_delete=models.CASCADE,related_name="orders")

    project_object=models.ManyToManyField(Project)

    order_id=models.CharField(max_length=100,null=True)

    is_paid=models.BooleanField(default=False)

    created_date=models.DateTimeField(auto_now_add=True)

    updated_date=models.DateTimeField(auto_now=True)

    is_active=models.BooleanField(default=True)

    total=models.FloatField(null=True)



#django signals
#post_save()
#pre_save()
#post_init()
from django.db.models.signals import post_save

def create_profile(sender,instance,created,*args,**kwargs):

    if created:

        UserProfile.objects.create(user_object=instance)


post_save.connect(receiver=create_profile,sender=User)


def create_basket(sender,instance,created,*args,**kwargs):

    if created:

        WishList.objects.create(owner=instance)
    
post_save.connect(receiver=create_basket,sender=User)


from django.core.validators import MinValueValidator,MaxValueValidator
class Reviews(models.Model):

    project_objects=models.ForeignKey(Project,on_delete=models.CASCADE,related_name="project_reviews")
    
    user_object=models.ForeignKey(User,on_delete=models.CASCADE)

    comment=models.TextField()

    
    rating=models.PositiveIntegerField(default=1,validators=[MinValueValidator(1),MaxValueValidator(5)])

    created_date=models.DateTimeField(auto_now_add=True)

    updated_date=models.DateTimeField(auto_now=True)

    is_active=models.BooleanField(default=True)




















