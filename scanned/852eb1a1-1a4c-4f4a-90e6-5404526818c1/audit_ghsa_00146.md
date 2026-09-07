# [M] Directory Traversal in augustine

## Summary
Severity: Medium
Advisory: GHSA-4wch-fwmx-cf47
CVE: CVE-2017-0930
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-09-18
Source: https://github.com/advisories/GHSA-4wch-fwmx-cf47
Type: github-advisory

## Affected
- npm: `augustine` — affected >=0

## Details
Affected versions of `augustine` resolve relative file paths, resulting in a directory traversal vulnerability. A malicious actor can use this vulnerability to access files outside of the intended directory root, which may result in the disclosure of private files on the vulnerable system.

## Proof of Concept
```http
GET //etc/passwd HTTP/1.1
host:foo
```


## Recommendation

No direct patch is available at this time. 

Currently, the best mitigation for this flaw is to use a different, functionally equivalent static file server package.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-0930
- https://hackerone.com/reports/296282
- https://github.com/advisories/GHSA-4wch-fwmx-cf47
- https://www.npmjs.com/advisories/559
