# [H] ALPINE-CVE-2020-24583

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-24583
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-09-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-24583
Type: osv

## Affected
- Alpine:v3.10: `py-django` — affected >=0 <1.11.29-r1
- Alpine:v3.9: `py-django` — affected >=0 <1.11.29-r1
- Alpine:v3.11: `py3-django` — affected >=0 <1.11.29-r1
- Alpine:v3.12: `py3-django` — affected >=0 <1.11.29-r1

## Details
An issue was discovered in Django 2.2 before 2.2.16, 3.0 before 3.0.10, and 3.1 before 3.1.1 (when Python 3.7+ is used). FILE_UPLOAD_DIRECTORY_PERMISSIONS mode was not applied to intermediate-level directories created in the process of uploading files. It was also not applied to intermediate-level collected static directories when using the collectstatic management command.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-24583
