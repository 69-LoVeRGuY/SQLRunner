from django.http import HttpResponse
from django.http import JsonResponse
from django.db import connection
import json

def home(request):
    return HttpResponse("Welcome to SQL Runner! Use /run_query/ to execute your SQL queries.")

def run_query(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET method is allowed'}, status=405)
    data = json.loads(request.body.decode('utf-8'))
    query = data.get('query')
    if not query:
        return JsonResponse({'error': 'No query provided'}, status=400)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            query_type = query.strip().split(" ",1)[0].lower()
            if query_type in ['select']:
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                return JsonResponse({'results': results}, status=200)
            elif query_type in ['insert', 'update', 'delete', 'create', 'alter', 'drop']:
                results = {'message': f'{query_type.capitalize()} executed successfully'}
                return JsonResponse(results, status=200)
            else:
                return JsonResponse({'error': 'Unsupported query type'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)