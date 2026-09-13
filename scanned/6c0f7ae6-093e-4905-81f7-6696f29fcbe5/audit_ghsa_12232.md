# [H] File Descriptor Leak Can Cause DoS Vulnerability in hapi

## Summary
Severity: High
Advisory: GHSA-cqr7-78pj-3g7j
CVE: CVE-2014-3742
CWE: CWE-400
Ecosystem: npm
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-cqr7-78pj-3g7j
Type: github-advisory

## Affected
- npm: `hapi` — affected >=2.0.0 <2.2.0

## Details
Versions 2.0.x and 2.1.x of hapi are vulnerable to a denial of service attack via a file descriptor leak. 

When triggered repeatedly, this leak will cause the server to run out of file descriptors and the node process to die. The effort required to take down a server depends on the process file descriptor limit. No other side effects or exploits have been identified.



## Recommendation

- Please upgrade to version 2.2.x or above as soon as possible.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3742
- https://github.com/spumko/hapi/issues/1427
- https://github.com/advisories/GHSA-cqr7-78pj-3g7j
- https://github.com/spumko/hapi
- https://www.npmjs.com/advisories/11
- http://www.openwall.com/lists/oss-security/2014/05/13/1
- http://www.openwall.com/lists/oss-security/2014/05/15/2
