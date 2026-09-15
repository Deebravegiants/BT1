# [M] safeurl-python contains Server-Side Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-jgh8-vchw-q3g7
CVE: CVE-2023-24622
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-01-27
Source: https://github.com/advisories/GHSA-jgh8-vchw-q3g7
Type: github-advisory

## Affected
- PyPI: `safeurl-python` — affected >=0 <1.2

## Details
### Description
In SafeURL it is possible to specify a list of domains that should be matched before a request is sent out. The regex used to compare domains did not work as intended.

### Impact
The regex used was:

`re.match("(?i)^%s" % domain, value)`

This has two problems, first that only the beginning and not the end of the string is anchored. Second, that a dot in the domain matches any character as part of regex syntax.

Therefore, an allowlist of ["victim.com"] could allow the domain "victimacomattacker.com" to be requested.

This has lower impact since the usual attacker aim in an SSRF is to request internal resources such as private IP addresses rather than an attacker's own domain. But, in a case where SafeURL had specifically been used to try to limit requests to a particular allowlist, say for example a PDF renderer, the finding would be more severe.

### Patches
Fixed in https://github.com/IncludeSecurity/safeurl-python/pull/5

### References
[Server-side request forgery (SSRF)](https://portswigger.net/web-security/ssrf)

## References
- https://github.com/IncludeSecurity/safeurl-python/security/advisories/GHSA-jgh8-vchw-q3g7
- https://github.com/IncludeSecurity/safeurl-python/pull/5/commits/42dd0c8e5fc84e17e1d3578d18aaea169eece474
- https://github.com/IncludeSecurity/safeurl-python
- https://github.com/pypa/advisory-database/tree/main/vulns/safeurl-python/PYSEC-2023-298.yaml
