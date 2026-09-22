# [H] Django vulnerable to Reflected File Download attack

## Summary
Severity: High
Advisory: GHSA-8x94-hmjh-97hq
CVE: CVE-2022-36359
CWE: CWE-494
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-11
Source: https://github.com/advisories/GHSA-8x94-hmjh-97hq
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0 <3.2.15
- PyPI: `Django` — affected >=4.0 <4.0.7

## Details
An issue was discovered in the HTTP FileResponse class in Django 3.2 before 3.2.15 and 4.0 before 4.0.7. An application is vulnerable to a reflected file download (RFD) attack that sets the Content-Disposition header of a FileResponse when the filename is derived from user-supplied input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36359
- https://github.com/django/django/commit/b3e4494d759202a3b6bf247fd34455bf13be5b80
- https://github.com/django/django/commit/b7d9529cbe0af4adabb6ea5d01ed8dcce3668fb3
- https://github.com/django/django/commit/bd062445cffd3f6cc6dcd20d13e2abed818fa173
- https://docs.djangoproject.com/en/4.0/releases/security
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2022-245.yaml
- https://groups.google.com/g/django-announce/c/8cz--gvaJr4
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HWY6DQWRVBALV73BPUVBXC3QIYUM24IK
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LTZVAKU5ALQWOKFTPISE257VCVIYGFQI
- https://security.netapp.com/advisory/ntap-20220915-0008
- https://www.debian.org/security/2022/dsa-5254
- https://www.djangoproject.com/weblog/2022/aug/03/security-releases
- http://www.openwall.com/lists/oss-security/2022/08/03/1
