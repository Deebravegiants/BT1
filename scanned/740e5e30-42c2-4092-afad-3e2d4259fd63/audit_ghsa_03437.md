# [H] SQL Injection via in django-debug-toolbar

## Summary
Severity: High
Advisory: GHSA-pghf-347x-c2gj
CVE: CVE-2021-30459
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-16
Source: https://github.com/advisories/GHSA-pghf-347x-c2gj
Type: github-advisory

## Affected
- PyPI: `django-debug-toolbar` — affected >=0.10.0 <1.11.1
- PyPI: `django-debug-toolbar` — affected >=2.0a1 <2.2.1
- PyPI: `django-debug-toolbar` — affected >=3.0a1 <3.2.1

## Details
### Impact
With Django Debug Toolbar attackers are able to execute SQL by changing the `raw_sql` input of the SQL explain, analyze or select forms and submitting the form.

**NOTE:** This is a high severity issue for anyone using the toolbar in a **production environment**.

Generally the Django Debug Toolbar team only maintains the latest version of django-debug-toolbar, but an exception was made because of the high severity of this issue.

### Patches
Please upgrade to one of the following versions, depending on the major version you're using:

- Version 1.x: [django-debug-toolbar 1.11.1](https://pypi.org/project/django-debug-toolbar/1.11.1/)
- Version 2.x: [django-debug-toolbar 2.2.1](https://pypi.org/project/django-debug-toolbar/2.2.1/)
- Version 3.x: [django-debug-toolbar 3.2.1](https://pypi.org/project/django-debug-toolbar/3.2.1/)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in the [django-debug-toolbar repo](https://github.com/jazzband/django-debug-toolbar/issues/new)  (Please NO SENSITIVE INFORMATION, send an email instead!)
* Email us at [security@jazzband.co](mailto:security@jazzband.co)

## References
- https://github.com/jazzband/django-debug-toolbar/security/advisories/GHSA-pghf-347x-c2gj
- https://nvd.nist.gov/vuln/detail/CVE-2021-30459
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-30459
- https://github.com/jazzband/django-debug-toolbar
- https://github.com/jazzband/django-debug-toolbar/releases
- https://github.com/pypa/advisory-database/tree/main/vulns/django-debug-toolbar/PYSEC-2021-10.yaml
- https://www.djangoproject.com/weblog/2021/apr/14/debug-toolbar-security-releases
