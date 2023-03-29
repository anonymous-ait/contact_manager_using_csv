from django.shortcuts import render
import csv
from io import TextIOWrapper
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ContactSerializer
from rest_framework import status
import json 
import pika

class ContactView(APIView):
    def post(self,request,*args,**kwargs):
        file= request.FILES.get('file')
        if not file :
            return Response({'error':"no file uploaded"},status= status.HTTP_400_BAD_REQUEST)
        text_file = TextIOWrapper(file, encoding='utf-8')
        reader= csv.DictReader(text_file)
        rows=[]
        for row in reader:
            serializer=ContactSerializer(data=row)
            if serializer.is_valid():
                rows.append(serializer.save())

            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        return Response({'success': 'contact list updated'},status=status.HTTP_201_CREATED)

        

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def update_contacts(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({'error': 'No file was uploaded.'}, status=400)
        
        # Read the CSV file and update the database
        contacts = []
        for line in file:
            row = line.decode('utf-8').strip().split(',')
            contact = {
                'name': row[0],
                'phone': row[1],
                'email': row[2],
            }
            contacts.append(contact)
        
        # Publish the contacts to the RabbitMQ queue
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='contacts')
        channel.basic_publish(exchange='', routing_key='contacts', body=json.dumps(contacts))
        connection.close()

        return JsonResponse({'success': 'Contacts uploaded successfully.'}, status=200)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)
