# [H] Denial-of-Service Memory Exhaustion in qs

## Summary
Severity: High
Advisory: GHSA-jjv7-qpx3-h62q
CVE: CVE-2014-7191
CWE: CWE-400
Ecosystem: npm
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-jjv7-qpx3-h62q
Type: github-advisory

## Affected
- npm: `qs` — affected >=0 <1.0.0

## Details
Versions prior to 1.0 of `qs` are affected by a denial of service condition. This condition is triggered by parsing a crafted string that deserializes into very large sparse arrays, resulting in the process running out of memory and eventually crashing.


## Recommendation

Update to version 1.0.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-7191
- https://github.com/visionmedia/node-querystring/issues/104
- https://github.com/raymondfeng/node-querystring/commit/43a604b7847e56bba49d0ce3e222fe89569354d8
- https://access.redhat.com/errata/RHSA-2016:1380
- https://exchange.xforce.ibmcloud.com/vulnerabilities/96729
- https://github.com/advisories/GHSA-jjv7-qpx3-h62q
- https://github.com/visionmedia/node-querystring
- https://www.npmjs.com/advisories/29
- http://secunia.com/advisories/60026
- http://secunia.com/advisories/62170
- http://www-01.ibm.com/support/docview.wss?uid=swg21685987
- http://www-01.ibm.com/support/docview.wss?uid=swg21687263
- http://www-01.ibm.com/support/docview.wss?uid=swg21687928
