# [M] HTTP Request Smuggling due to accepting space before colon

## Summary
Severity: Medium
Program: Node.js
Weakness: HTTP Request Smuggling
Reporter: mkg
State: resolved
Disclosed: 2021-10-20T14:58:11.063Z
CVE: CVE-2021-22959
Source: https://hackerone.com/reports/1238709

## Details
**Summary:**
The ``llhttp`` parser in the ``http``module in Node 16.3.0 accepts requests with a space (SP) right after the header name before the colon. This can lead to HTTP Request Smuggling (HRS).

**Description:**
When Node receives the following request:

```
GET / HTTP/1.1
Host: localhost:5000
Content-Length : 5

hello
```

It interprets the request as having the body `hello`. Here is the relevant section of the code: https://github.com/nodejs/llhttp/blob/master/src/llhttp/http.ts#L410-L415

How could this lead to HRS? Imagine that Node is placed behind a proxy which ignores the CL header with a space before the colon, but forwards it as is. Then the following attack can be performed:

```
GET / HTTP/1.1
Host: localhost:5000
Content-Length : 23

GET / HTTP/1.1
Dummy: GET /smuggled HTTP/1.1
Host: localhost:5000

```

The proxy would see the first and the second GET-request. But Node would see the first and the third GET-request.

## Steps To Reproduce:

We don't know of any proxy that behaves this way, but here is how to show that Node is behaving in the described way. Run the following code like this: `node app.js`

```js
const http = require('http');

```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1238709_
