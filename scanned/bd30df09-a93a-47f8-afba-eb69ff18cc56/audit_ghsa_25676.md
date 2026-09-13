# [H] Improper Authentication in django-mfa3

## Summary
Severity: High
Advisory: GHSA-3r7g-wrpr-j5g4
CVE: CVE-2022-24857
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-3r7g-wrpr-j5g4
Type: github-advisory

## Affected
- PyPI: `django-mfa3` — affected >=0 <0.5.0

## Details
### Impact

django-mfa3 is a library that implements multi factor authentication for the django web framework. It achieves this by modifying the regular login view. Django however has a second login view for its admin area. This second login view was not modified, so the multi factor authentication can be bypassed.

You are affected if you have activated both django-mfa3 (< 0.5.0) and django.contrib.admin and have not taken any other measures to prevent users from accessing the admin login view.

### Patches

The issue has been fixed in django-mfa3 0.5.0.

### Workarounds

It is possible to work around the issue by overwriting the admin login route, e.g. by adding the following URL definition *before* the admin routes:

    url('admin/login/', lambda request: redirect(settings.LOGIN_URL)

### References

- [django-mfa3 changelog](https://github.com/xi/django-mfa3/blob/main/CHANGES.md#050-2022-04-15)

## References
- https://github.com/xi/django-mfa3/security/advisories/GHSA-3r7g-wrpr-j5g4
- https://nvd.nist.gov/vuln/detail/CVE-2022-24857
- https://github.com/xi/django-mfa3/commit/32f656e22df120b84bdf010e014bb19bd97971de
- https://github.com/pypa/advisory-database/tree/main/vulns/django-mfa3/PYSEC-2022-192.yaml
- https://github.com/xi/django-mfa3
- https://github.com/xi/django-mfa3/blob/main/CHANGES.md#050-2022-04-15
- https://security.netapp.com/advisory/ntap-20220609-0003
