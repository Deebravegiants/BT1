# [M] Python Social Auth - Django has unsafe account association 

## Summary
Severity: Medium
Advisory: GHSA-wv4w-6qv2-qqfg
CVE: CVE-2025-61783
CWE: CWE-290, CWE-303
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-09
Source: https://github.com/advisories/GHSA-wv4w-6qv2-qqfg
Type: github-advisory

## Affected
- PyPI: `social-auth-app-django` — affected >=0 <5.6.0

## Details
### Impact

Upon authentication, the user could be associated by e-mail even if the `associate_by_email` pipeline was not included. This could lead to account compromise when a third-party authentication service does not validate provided e-mail addresses or doesn't require unique e-mail addresses.

### Patches

* https://github.com/python-social-auth/social-app-django/pull/803

### Workarounds

Review the authentication service policy on e-mail addresses; many will not allow exploiting this vulnerability.

## References
- https://github.com/python-social-auth/social-app-django/security/advisories/GHSA-wv4w-6qv2-qqfg
- https://nvd.nist.gov/vuln/detail/CVE-2025-61783
- https://github.com/python-social-auth/social-app-django/issues/220
- https://github.com/python-social-auth/social-app-django/issues/231
- https://github.com/python-social-auth/social-app-django/issues/634
- https://github.com/python-social-auth/social-app-django/pull/803
- https://github.com/python-social-auth/social-app-django/commit/10c80e2ebabeccd4e9c84ad0e16e1db74148ed4c
- https://github.com/python-social-auth/social-app-django
