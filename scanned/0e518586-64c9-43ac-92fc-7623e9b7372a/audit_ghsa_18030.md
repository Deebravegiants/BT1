# [H] Versity panic induced by AWS chunked data sent to port

## Summary
Severity: High
Advisory: GHSA-v2ch-c8v8-fgr7
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-08-29
Source: https://github.com/advisories/GHSA-v2ch-c8v8-fgr7
Type: github-advisory

## Affected
- Go: `github.com/versity/versitygw` — affected >=0 <1.0.17

## Details
Sending AWS chunk data with no Content-Length HTTP header causes the panic, every time. 

### Reproduction

Setup versity server running on port 7071, no SSL (for ease of packet tracing with tshark). Problem can be reproduced with or without SSL on the versity end. 

Use nginx to reverse proxy on port 7070. This does have to be SSL enabled for the repro to occur. nginx config: 

```
upstream tony_versity {
        server 127.0.0.1:7071;
        keepalive 15;
}

server {
    listen       7070 ssl ;
    access_log  /var/log/nginx/tony_versity_proxy.access.log;
    error_log /var/log/nginx/tony_versity_proxy.error.log;

    # Allow any size file to be uploaded.
    client_max_body_size 0;
    # Allow special characters in headers
    ignore_invalid_headers off;
    # Disable buffering
    proxy_buffering off;
    proxy_request_buffering off;

    # Load configuration files for the default server block.
    include /etc/nginx/default.d/*.conf;

    ssl_certificate "/WS/TEMP/lh.crt";
    ssl_certificate_key "/WS/TEMP/lh.key";
    ssl_session_cache shared:SSL:1m;
    ssl_session_timeout  10m;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        allow all;
        proxy_pass http://127.0.0.1:7071;
        proxy_http_version 1.1;
        proxy_read_timeout 120;
        proxy_connect_timeout 300;

        # Set headers
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Transfer-Encoding "";

        # CORS headers
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization,Accept,ETag,Origin,DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Content-Range,Range' always;
        add_header 'Access-Control-Allow-Methods' 'GET,POST,OPTIONS,PUT,DELETE,PATCH' always;
        add_header 'Access-Control-Expose-Headers' 'ETag, Content-Length, Content-Range' always;

        # Optional security headers
        add_header X-Content-Type-Options nosniff always;
        add_header X-Frame-Options DENY always;
        add_header Referrer-Policy no-referrer always;

        # Preflight (OPTIONS) handler
        if ($request_method = OPTIONS) {
            add_header Access-Control-Allow-Origin '*' always;
            add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS, PUT, DELETE, PATCH' always;
            add_header Access-Control-Allow-Headers 'Authorization,Accept,ETag,Origin,DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Content-Range,Range' always;
            add_header Access-Control-Expose-Headers 'ETag, Content-Length, Content-Range' always;
            add_header Content-Type text/plain;
            add_header Content-Length 0;
            return 204;
        }
    }
}
```

Use aws s3 cp to copy a large file (one that will trigger multipart upload) into versity via the nginx proxy on port 7070. AWS CLI must be version 2 for the repro to occur. Connecting directly to versity on port 7070 does not trigger the repro.

 
### Initial crash analysis

The versity server enters a panic exception in function `HashReader` (csum-reader.go). The panic is due to a null value in the field r which should be a pointer to an io.Reader. 

The reason this field is blank goes back to code in the `fasthttp` library, `ContinueReadBodyStream`. This function exits prematurely if the incoming request `ContentLength` field is set to `-2`, and therefore does not set up an io.Reader in the request context structure. 

`-2` is not a valid content-length for an HTTP message, it is a special value used internally by the `fasthttp` module. (Unfortunately the author hard coded the value rather than using a meaningful macro, which would have aided the understanding here. )

The reason for the `-2` can be found in function `parseHeaders`(headers.go in fasthttp). The header struct content length is set to `-2` at the start of the function, and will be overwritten if an HTTP content-length header is encountered during the parsing. If no such header is present in the request, it stays as `-2` with the later result of skipping the creation of an io.Reader. Seems reasonable - no content, no need for a reader? (Note that the presence of content-length triggers body reader creation even if the value is 0.) The fasthttp code replaces the illegal `-2` value with `0` before passing the request up to Versity. 

So the pathway of this crash is receiving a request with no content-length, which means no body reader is set in the request context structure, but Versity tries to read anyway in the hash routines. 

This pathology was confirmed by artificially creating a content-length on all incoming packets that didn’t have one, the outcome being that this panic did not occur, although the overall upload still reported failure (I didn’t go into exactly why as the point had been proven).

 
### Further Analysis

The question becomes why there is no HTTP content-length header in this request. The answer to this is that the large transfer is being done using AWS chunking. Wireshark shows the packet structure. There is an initial POST request with content-length zero:
Hypertext Transfer Protocol
```
    POST /ttt/f2?uploads HTTP/1.1\r\n
    Host: 127.0.0.1:7070\r\n
    X-Real-IP: 127.0.0.1\r\n
    X-Forwarded-For: 127.0.0.1\r\n
    X-Forwarded-Proto: https\r\n
    Connection: close\r\n
    Content-Length: 0\r\n
    Accept-Encoding: identity\r\n
    x-amz-checksum-algorithm: CRC64NVME\r\n
     [truncated]User-Agent: aws-cli/2.27.52 md/awscrt#0.26.1 ua/2.1 os/linux#4.18.0-553.16.1.el8_10.x86_64 md/arch#x86_64 lang/python#3.13.4 md/pyimpl#CPython m/E,Z,N,G,b cfg/retry-mode#standard md/installer#exe md/distrib#rhel.8 md/prompt#off
    X-Amz-Date: 20250718T105915Z\r\n
    X-Amz-Content-SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\r\n
     [truncated]Authorization: AWS4-HMAC-SHA256 Credential=AKIA000000000000000/20250718/us-east-1/s3/aws4_request, SignedHeaders=host;x-amz-checksum-algorithm;x-amz-content-sha256;x-amz-date, Signature=cd9f6a85ae2dd964aa44274d7d0642c51f8b32584
    \r\n
    [Full request URI: http://127.0.0.1:7070/ttt/f2?uploads]
    [HTTP request 1/1]
    [Response in frame: 6]
```
.. followed soon after by a PUT request with ‘content-encdoding: aws-chunked’. According to the AWS documentation, this encoding is used when the size of the upload is not known in advance, and a content-length header is expressly forbidden. AWS supplies other headers with size information, but these are not recognised by fasthttp.
Hypertext Transfer Protocol
```
    PUT /ttt/f2?uploadId=7170abfd-e29a-40fe-bd34-31b434cc1b6b&partNumber=1 HTTP/1.1\r\n
    Host: 127.0.0.1:7070\r\n
    X-Real-IP: 127.0.0.1\r\n
    X-Forwarded-For: 127.0.0.1\r\n
    X-Forwarded-Proto: https\r\n
    Connection: close\r\n
    Accept-Encoding: identity\r\n
    x-amz-sdk-checksum-algorithm: CRC64NVME\r\n
     [truncated]User-Agent: aws-cli/2.27.52 md/awscrt#0.26.1 ua/2.1 os/linux#4.18.0-553.16.1.el8_10.x86_64 md/arch#x86_64 lang/python#3.13.4 md/pyimpl#CPython m/E,Z,N,G,b,W cfg/retry-mode#standard md/installer#exe md/distrib#rhel.8 md/prompt#o
    Content-Encoding: aws-chunked\r\n
    X-Amz-Trailer: x-amz-checksum-crc64nvme\r\n
    X-Amz-Decoded-Content-Length: 8388608\r\n
    X-Amz-Date: 20250718T105915Z\r\n
    X-Amz-Content-SHA256: STREAMING-UNSIGNED-PAYLOAD-TRAILER\r\n
     [truncated]Authorization: AWS4-HMAC-SHA256 Credential=AKIA000000000000000/20250718/us-east-1/s3/aws4_request, SignedHeaders=content-encoding;host;x-amz-content-sha256;x-amz-date;x-amz-decoded-content-length;x-amz-sdk-checksum-algorithm;x-
    \r\n
    [Full request URI: http://127.0.0.1:7070/ttt/f2?uploadId=7170abfd-e29a-40fe-bd34-31b434cc1b6b&partNumber=1]
    [HTTP request 1/1]
```
 

The initial response to the first POST request appears to be identical in both the direct and via nginx traces:
DIRECT:
Hypertext Transfer Protocol
```
    HTTP/1.1 200 OK\r\n
    Server: VERSITYGW\r\n
    Date: Fri, 18 Jul 2025 11:01:02 GMT\r\n
    Content-Type: application/xml\r\n
    Content-Length: 240\r\n
    X-Amz-Checksum-Algorithm: CRC64NVME\r\n
    Connection: close\r\n
    \r\n
    [HTTP response 1/1]
    [Time since request: 0.024200152 seconds]
    [Request in frame: 4]
    [Request URI: http://127.0.0.1:7071/ttt/f2?uploads]
    File Data: 240 bytes
```
 
VIA NGINX PROXY:
Hypertext Transfer Protocol
```
    HTTP/1.1 200 OK\r\n
    Server: VERSITYGW\r\n
    Date: Fri, 18 Jul 2025 10:59:15 GMT\r\n
    Content-Type: application/xml\r\n
    Content-Length: 240\r\n
    X-Amz-Checksum-Algorithm: CRC64NVME\r\n
    Connection: close\r\n
    \r\n
    [HTTP response 1/1]
    [Time since request: 0.024228406 seconds]
    [Request in frame: 4]
    [Request URI: http://127.0.0.1:7070/ttt/f2?uploads]
    File Data: 240 bytes
```
### What is yet to know

Wireshark traces show that the exact same AWS command results in a different upload pattern when connecting directly to Versity (with or without SSL) rather than going through nginx. There is a similar initial POST but followed by a stream of raw TCP with ‘100 - Continue’ responses from the server. There is no PUT request with content-encoding aws-chunked:
Hypertext Transfer Protocol
```
    POST /ttt/f2?uploads HTTP/1.1\r\n
    Host: 127.0.0.1:7071\r\n
    Accept-Encoding: identity\r\n
    x-amz-checksum-algorithm: CRC64NVME\r\n
     [truncated]User-Agent: aws-cli/2.27.52 md/awscrt#0.26.1 ua/2.1 os/linux#4.18.0-553.16.1.el8_10.x86_64 md/arch#x86_64 lang/python#3.13.4 md/pyimpl#CPython m/b,G,Z,N,E cfg/retry-mode#standard md/installer#exe md/distrib#rhel.8 md/prompt#off
    X-Amz-Date: 20250718T110102Z\r\n
    X-Amz-Content-SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\r\n
     [truncated]Authorization: AWS4-HMAC-SHA256 Credential=AKIA000000000000000/20250718/us-east-1/s3/aws4_request, SignedHeaders=host;x-amz-checksum-algorithm;x-amz-content-sha256;x-amz-date, Signature=925d2f18f7f88ab7826ae7faf61f95b17033f5e19
    Content-Length: 0\r\n
    \r\n
    [Full request URI: http://127.0.0.1:7071/ttt/f2?uploads]
    [HTTP request 1/1]
    [Response in frame: 6]
```
It is unclear why AWS switches to the chunked mode when connecting through nginx. It is possible that changes to the nginx config could work around this, however the Versity behaviour remains a problem. At the very least this is a potential DDOS vulnerability. There is no structured exception handling in Versity at all and no defensive coding such as verifying callbacks are non-null before attempting to use them.

## References
- https://github.com/versity/versitygw/security/advisories/GHSA-v2ch-c8v8-fgr7
- https://github.com/versity/versitygw/issues/1418
- https://github.com/versity/versitygw/commit/0972af078325ab5c6acd37abffe6bea345ac7db0
- https://github.com/versity/versitygw
