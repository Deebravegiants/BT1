# [C] ALPINE-CVE-2019-14234

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-14234
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-14234
Type: osv

## Affected
- Alpine:v3.10: `py-django` — affected >=0 <1.11.23-r0
- Alpine:v3.7: `py-django` — affected >=0 <1.11.23-r0
- Alpine:v3.8: `py-django` — affected >=0 <1.11.23-r0
- Alpine:v3.9: `py-django` — affected >=0 <1.11.23-r0
- Alpine:v3.11: `py3-django` — affected >=0 <1.11.23-r0
- Alpine:v3.12: `py3-django` — affected >=0 <1.11.23-r0

## Details
An issue was discovered in Django 1.11.x before 1.11.23, 2.1.x before 2.1.11, and 2.2.x before 2.2.4. Due to an error in shallow key transformation, key and index lookups for django.contrib.postgres.fields.JSONField, and key lookups for django.contrib.postgres.fields.HStoreField, were subject to SQL injection. This could, for example, be exploited via crafted use of "OR 1=1" in a key or index name to return all records, using a suitably crafted dictionary, with dictionary expansion, as the **kwargs passed to the QuerySet.filter() function.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-14234
