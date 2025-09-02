from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    resp = exception_handler(exc, context)
    if resp is None:
        return Response({'status':'error','message':'Server error','errors':{'detail':[str(exc)]}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    data = {'status':'error','message':'Validation failed' if resp.status_code==400 else 'Error', 'errors': {}}
    if isinstance(resp.data, dict):
        for k, v in resp.data.items():
            data['errors'][k] = v
    else:
        data['errors'] = {'detail': resp.data}
    return Response(data, status=resp.status_code)
