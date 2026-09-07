# [M] CKAN has CSRF exemption primed by anonymous requests

## Summary
Severity: Medium
Advisory: GHSA-mcvf-jxcw-vj73
CVE: CVE-2026-41255
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-mcvf-jxcw-vj73
Type: github-advisory

## Affected
- PyPI: `ckan` — affected >=2.10.0 <2.10.10
- PyPI: `ckan` — affected >=2.11.0 <2.11.5

## Details
Views can be marked as exempt from CSRF protection 

Access to the views via tokens or unauthenticated requests marked the endpoint as not requiring CSRF protection. 

The marking was a member variable in flask-wtf.csrf.CSRFProtect(), which was stored as a module level variable in the flask_app middleware. Thsi API was never intended for request level changes, it is primarily a decorator for static configuration. 

An unauthenticated request could hit a protected endpoint, exempting it from CSRF protection for the life of the particular server process. (e.g. one worker of uwsgi).

This could be leveraged with XSS to perform actions using other user's credentials.

### References

* [Vulnerability report](https://github.com/Shirshaw64p/security-advisories/tree/main/CVE-2026-41255) by @Shirshaw64p (original reporter)

## References
- https://github.com/ckan/ckan/security/advisories/GHSA-mcvf-jxcw-vj73
- https://nvd.nist.gov/vuln/detail/CVE-2026-41255
- https://docs.ckan.org/en/2.10/changelog.html#v-2-10-10-2026-04-29
- https://docs.ckan.org/en/2.11/changelog.html#v-2-11-5-2026-04-29
- https://github.com/Shirshaw64p/security-advisories/tree/main/CVE-2026-41255
- https://github.com/ckan/ckan
