from django.db import models
import datetime

def upload_to(instance, filename):
    date_string = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    return './brazzers-%s.jpg' % date_string 

class ProImage(models.Model):
	image = models.ImageField(upload_to=upload_to)
	created_date = models.DateTimeField(auto_now_add=True)

