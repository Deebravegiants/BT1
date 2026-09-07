# [M] Flask-AppBuilder Open Redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-624f-cqvr-3qw4
CVE: CVE-2021-32805
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-09-08
Source: https://github.com/advisories/GHSA-624f-cqvr-3qw4
Type: github-advisory

## Affected
- PyPI: `Flask-AppBuilder` — affected >=0 <3.3.2

## Details
### Impact
If using Flask-AppBuilder OAuth, an attacker can share a carefully crafted URL with a trusted domain for an application built with Flask-AppBuilder, this URL can redirect a user to a malicious site. This is an open redirect vulnerability 

### Patches
Install Flask-AppBuilder 3.2.2 or above

### Workarounds
Filter HTTP traffic containing `?next={next-site}` where the `next-site` domain is different from the application you are protecting

## References
- https://github.com/dpgaspar/Flask-AppBuilder/security/advisories/GHSA-624f-cqvr-3qw4
- https://nvd.nist.gov/vuln/detail/CVE-2021-32805
- https://github.com/dpgaspar/Flask-AppBuilder/commit/6af28521589599b1dbafd6313256229ee9a4fa74
- https://github.com/dpgaspar/Flask-AppBuilder
- https://github.com/dpgaspar/Flask-AppBuilder/releases/tag/v3.3.2
- https://github.com/pypa/advisory-database/tree/main/vulns/flask-appbuilder/PYSEC-2021-359.yaml
- https://pypi.org/project/Flask-AppBuilder
