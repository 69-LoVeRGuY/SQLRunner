from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
import json

def home(request):
    return HttpResponse("Welcome to SQL Runner! Use /run_query/ to execute your SQL queries.")

@require_POST
@csrf_exempt
def run_query(request):
    if not request.body:
        return JsonResponse({'Request body cannot be empty'}, status=400)
    
    data = json.loads(request.body.decode('utf-8'))
    query = data.get('query')
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
    


def get_table_names(request):
    tables = []
    try:
        with connection.cursor() as cursor:
            table_names = connection.introspection.table_names(cursor)
            for tableName in table_names:
                if '_' in tableName:
                    continue
                else:
                    tables.append(tableName)
            return JsonResponse({'tables': tables}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_table_schema(request):
    schema = {}
    try:
        with connection.cursor() as cursor:
            table_names = connection.introspection.table_names(cursor)
            for table in table_names:
                if '_' in table:
                    continue
                cursor.execute(f"SELECT * FROM {table}  LIMIT 1")
                sample_data = cursor.fetchall()
                schema[table] = []
                details =  connection.introspection.get_table_description(cursor, table)
                for detail in details:
                    try:
                        django_types = connection.introspection.get_field_type(detail.type_code, detail)
                    except Exception as e:
                        django_types = str(detail.type_code)
                    schema[table].append({
                        'name': detail.name,
                        'type': django_types[:-5],
                    })
                schema[table].append({
                    'sample': sample_data
                })
        return JsonResponse({'schema': schema}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)