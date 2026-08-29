# [C] Denial of Service by resource exhaustion CWE-400 due to unfinished HTTP/1.1 requests

## Summary
Severity: Critical (CVSS 9.3)
Program: Node.js
Weakness: Uncontrolled Resource Consumption
Reporter: shogunpanda
State: resolved
Disclosed: 2020-10-17T19:24:45.481Z
CVE: CVE-2020-8251
Source: https://hackerone.com/reports/868834

## Details
**Summary:** Node.js is vulnerable to HTTP denial of service (DOS) attacks based on delayed requests submission which can make the server unable to accept new connections.

**Description:**

An attacker can open an arbitrary number of HTTP connections and keep the server busy by never completing the request phase.

Node.js only has two requests timeouts:

1. [server.timeout](https://nodejs.org/docs/latest-v12.x/api/http.html#http_server_timeout) that controls the maximum number of milliseconds the socket can be idle. This also includes the server processing time. 
2. [server.headersTimeout](https://nodejs.org/docs/latest-v13.x/api/http.html#http_server_headerstimeout) (Added in Node 11.3.0), that controls the maximum number of milliseconds allowed to receive the full request headers before timing out.

Handling of request bodies is specific to the application code and core Node.js never consumes or parses the request bodies. 

Currently, the body parsing and handling is performed by the following modules:
* [fastify](https://www.fastify.io/)
* [restify](https://restify.com/)
* [busboy](https://github.com/mscdex/busboy), used by [fastify-multpart](https://github.com/fastify/fastify-multipart/) and [multer](https://github.com/expressjs/multer)
* [raw-body](https://github.com/stream-utils/raw-body), used by [body-parser](https://github.com/expressjs/body-parser)

All of the modules above are vulnerable to the attack.

If part of the body is already sent, the body parsing modules above can be patched to impose a request body sending timeout and therefore mitigate the attack.

The application unfortunately can not completely handle this attack. If the attacker never starts sending the body after completing the submission of the headers, the application code is never invoked. 

Prior to Node.js 13.0.0, the default timeout for a request was 2 minutes, which is a countermeasure against this attack.
Starting with Node.js 13.0.0 instead, the default timeout has been changed to be 0 (which means no timeout) in order to address serverless deployments where long running requests are needed. Since the socket is never considered idle, the application is completely vulnerable to the attack.

While `server.headersTimeout` is able to detect a slow request, it is only effective if the delay happens during the headers phase (like in Slowloris attacks). If the attacker delays the start of the headers, the start of body sending or sends the body very slow without resulting in an idle socket, the attack is not detected.

In the long run an unprotected server will have a lot of pending requests to handle. At some point it will reach the open connections limit and therefore will not be able to serve additional requests, resulting in a Denial of Service.

## Steps To Reproduce:

1. From one or more attacking sources, open one or more HTTP connections to the target server
2. For each of the connection in step 1
     2.1. (Optional) Wait a certain amount of time before sending the first request header.
     2.2 Send all request headers with regular pausing.

_Trimmed to 38 lines — full report: https://hackerone.com/reports/868834_
