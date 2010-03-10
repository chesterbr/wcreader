# coding=UTF-8

from django.db import models

class Comic(models.Model):
	name = models.CharField(max_length=255)
	next_button_xpath = models.CharField(max_length=500)
	next_button_expected_html = models.CharField(max_length=2000)
	
	def __unicode__(self):
		return self.name

class Episode(models.Model):
	comic = models.ForeignKey(Comic)
	order = models.IntegerField()
	title = models.CharField(max_length=500)
	url = models.CharField(max_length=2000)
	
class User(models.Model):
	openid = models.CharField(max_length=2000)
	
# Representar no user uma coleção de comics, onde cada um terá:
# - status: favorito, inativo, that kind of stuff
# - ponteiro para o último episode lido
# Opcional, decidir: - coleção dos episódios já lidos (é legal pra poder fazer um checklist, mas
# torna a escalabilidade mais complicada)