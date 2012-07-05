import re
import cStringIO
import datetime
import urllib
from PIL import Image
from django import forms
from django.conf import settings
from django.core.files.base import ContentFile
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from overlay import overlay as overlay_raw
from core.models import ProImage, upload_to

class UploadForm(forms.ModelForm):

	url = forms.URLField(required = False)

	def __init__(self, *args, **kwargs):
		super(UploadForm, self).__init__(*args, **kwargs)
		if 'image' in self.fields:
			self.fields['image'].required = False

	class Meta:
		model = ProImage


	def clean_url(self):
 		data = self.cleaned_data['url']
		if self.cleaned_data.get('image', None) is not None:
			return None
		
		if data == u'':
			return None

		if not re.search(r'\.jpe?g$', data):
			raise forms.ValidationError("Doesn't look like an image URL to me")

		# Always return the cleaned data, whether you have changed it or
		# not.
		return data

	def clean(self):
		cleaned_data = self.cleaned_data
		url_present = False
		image_present = False

		if 'url' in cleaned_data and cleaned_data['url'] is not None:
			url_present = True

		if 'image' in cleaned_data and cleaned_data['image'] is not None:
			image_present = True
			if 'url' in cleaned_data:
				del cleaned_data['url']

		# check at least one is filled
		if url_present == False and image_present == False:
			raise forms.ValidationError("Please upload an image or enter a valid URL!")

		return cleaned_data

def main(request):

	form = UploadForm()

	if request.method == 'POST':

		form = UploadForm(request.POST, request.FILES)

		if form.is_valid():
			use_uploaded = 'image' in form.cleaned_data and form.cleaned_data['image'] is not None
			if use_uploaded:
				image_data = form.cleaned_data['image'].file
			else:
				# assume we have a URL for a jpeg
				try:
					img_file = urllib.urlopen(form.cleaned_data['url'])
				except IOError, e:
					return HttpResponse("Sorry, I buggered something up")
				image_data = cStringIO.StringIO(img_file.read())

			uploaded_image = Image.open(image_data)

			overlay = Image.open(cStringIO.StringIO(overlay_raw))
	
			# make it just 1200 wide/high max
			uploaded_image.thumbnail((1200,1200), Image.ANTIALIAS)
			img_w, img_h= uploaded_image.size
			
			o_w, o_h = overlay.size
			off_w = (img_w / 2) - (o_w / 2)
			uploaded_image.paste(overlay, (off_w, img_h - 200), overlay)

			# 'save' image data to new filey-string object and shove that into the form cleaned_data
			fh = cStringIO.StringIO()
			uploaded_image.save(fh, format="JPEG")
			if use_uploaded:
				form.cleaned_data['image'].file = fh
				pro_image = form.save()
			else:
				# work out the path
				image_path = getattr(settings, 'MEDIA_ROOT') + upload_to(None,None)

				# make a content file object
				fh.seek(0)
				file_content = ContentFile(fh.read())

				# mash them together			
				pro_image = ProImage()
				pro_image.image.save(image_path, file_content)
				pro_image.save()

			return HttpResponseRedirect(pro_image.image.url)

        request_context = RequestContext(request, {'form': form})
	return render_to_response('base.html', request_context)

