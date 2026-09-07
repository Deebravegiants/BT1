# [M] Open redirect vulnerability in Flask-Security-Too

## Summary
Severity: Medium
Advisory: GHSA-672h-6x89-76m5
CVE: CVE-2023-49438
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-12-27
Source: https://github.com/advisories/GHSA-672h-6x89-76m5
Type: github-advisory

## Affected
- PyPI: `Flask-Security-Too` — affected >=0 <5.3.3

## Details
An open redirect vulnerability in the python package Flask-Security-Too <=5.3.2 allows attackers to redirect unsuspecting users to malicious sites via a crafted URL by abusing the ?next parameter on the /login and /register routes.

Flask-Security-Too contains logic to validate that the URL specified within the next parameter is either relative or has the same network location as the requesting URL in an attempt to prevent open redirections. Previously known examples that bypassed the validation logic such as `https://example/login?next=\\\\\\github.com` were patched in version 4.1.0

However, examples such as `https://example/login?next=/\\github.com` and `https://example/login?next=\\/github.com` were discovered due to how web browsers normalize slashes in URLs, which makes the package vulnerable through version <=5.3.2

Additionally, with Werkzeug >=2.1.0 the autocorrect_location_header configuration was changed to False - which means that location headers in redirects are relative by default. Thus, this issue may impact applications that were previously not impacted, if they are using Werkzeug >=2.1.0 as the WSGI layer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49438
- https://github.com/Flask-Middleware/flask-security/commit/8b5abc4d4db9926a3d76b34b8b03255effb5e712
- https://github.com/Flask-Middleware/flask-security
- https://github.com/brandon-t-elliott/CVE-2023-49438
- https://github.com/pypa/advisory-database/tree/main/vulns/flask-security-too/PYSEC-2023-248.yaml
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6HCYH377TPUMUHELPI36PDS2ZM4VFIXM
