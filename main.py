import ssl
import aiohttp
import logging
import sys
from aiohttp import web
import json

logger = logging.getLogger("mitm")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# change-it
HOST = "my-website.com"
IP = "1.2.3.4"

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain('cert.pem', 'key.pem')

ssl_context_target = ssl.create_default_context()
ssl_context_target.check_hostname = False
ssl_context_target.verify_mode = ssl.CERT_NONE

async def handle(request):
    async with aiohttp.ClientSession() as session:
        logger.info(f"{request.method} - {request.rel_url}")
        async with session.request(
            request.method,
            "https://" + IP + str(request.rel_url),
            headers=dict(request.headers) | {"Host": HOST},
            data=await request.read(),
            ssl=ssl_context_target,
            chunked=None
        ) as resp:
              body=await resp.content.read(-1)
              headers=dict(resp.headers)
              headers.pop('Transfer-Encoding',None)
              headers.pop('Content-Encoding',None)
              if request.method=='POST':
                # change-it
                if request.rel_url.path.startswith('/path/to/endpoint'):
                  logger.info(f"Modifying response for {request.rel_url}")
                  try:
                      data=json.loads(body)
                      # change-it
                      data['key']="value"
                      body=json.dumps(data).encode('utf-8')
                      headers['Content-Length']=str(len(body))
                  except Exception as e:
                      logger.error(f"Error modifying response: {e}")
                # change-it
                if request.rel_url.path.startswith('/path/to/another/endpoint'):
                  logger.info(f"Modifying response for {request.rel_url}")
                  try:
                      body=json.dumps(True).encode('utf-8')
                      headers['Content-Length']=str(len(body))
                  except Exception as e:
                      logger.error(f"Error modifying response: {e}")
              return web.Response(
                  body=body,
                  status=resp.status,
                  headers=headers
              )

app = web.Application()
app.router.add_route('*', '/{tail:.*}', handle)

web.run_app(app, port=443, ssl_context=ssl_context) 
