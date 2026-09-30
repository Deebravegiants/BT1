# [C] API Admin Auth Weakness in tomato

## Summary
Severity: Critical
Advisory: GHSA-9vxc-g2jx-qj3p
CVE: CVE-2013-7379
CWE: CWE-287
Ecosystem: npm
Published: 2020-08-31
Source: https://github.com/advisories/GHSA-9vxc-g2jx-qj3p
Type: github-advisory

## Affected
- npm: `tomato` — affected >=0 <0.0.6

## Details
Versions of `tomato` prior to 0.0.6 are affected by a somewhat complex authentication bypass vulnerability in the admin service when only a single access key is configured on the server. The vulnerability allows an attacker to guess the password for the admin service, no matter how complex that password is, in less than 200 requests.


## Details
The tomato API has an admin service that is enabled by setting up an `access_key` in the config options. This `access_key` is intended to protect the API admin from unauthorized access.


Tomato verifies the `access_key` by checking to see if the server `access_key` incorporates the user provided value at any location. This allows an attacker to provide a single character as an `access_key`, and so long as the server key contains at least one instance of that character it will be considered a valid key.

## Proof of Concept
This is the snippet of code that does the comparison to authorize requests.

```
if (access_key && config.master.api.access_key.indexOf(access_key) !== -1) {
```

For an access_key that is set to anything that includes the letter 'a' the following request would be authorized.

```
$ curl -X POST "http://localhost:8081/api/exec" -H "Content-Type: application/json" -d @test -H "access-key: a"
{
 "cmd": "ls",
 "path": ".",
 "stdout": "app.js\nconfig.js\nlog\nnode_modules\nserver.js\n",
 "stderr": ""
}
```



## Recommendation

Update to version 0.0.6 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7379
- https://github.com/leizongmin/tomato/commit/9e427d524e04a905312a3294c85e939ed7d57b8c
- https://github.com/leizongmin/tomato
- https://www.npmjs.com/advisories/38
- http://www.openwall.com/lists/oss-security/2014/05/13/1
- http://www.openwall.com/lists/oss-security/2014/05/15/2
