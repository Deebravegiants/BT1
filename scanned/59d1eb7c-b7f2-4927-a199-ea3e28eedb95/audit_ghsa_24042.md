# [H] Django Image Field Vulnerable to Image Decompression Bombs

## Summary
Severity: High
Advisory: GHSA-59w8-4wm2-4xw8
CVE: CVE-2012-3443
CWE: CWE-20, CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-59w8-4wm2-4xw8
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0 <1.3.2
- PyPI: `Django` — affected >=1.4 <1.4.1

## Details
The `django.forms.ImageField` class in the form system in Django before 1.3.2 and 1.4.x before 1.4.1 completely decompresses image data during image validation, which allows remote attackers to cause a denial of service (memory consumption) by uploading an image file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-3443
- https://github.com/django/django/commit/9ca0ff6268eeff92d0d0ac2c315d4b6a8e229155
- https://github.com/django/django/commit/da33d67181b53fe6cc737ac1220153814a1509f6
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2012-3.yaml
- https://www.debian.org/security/2012/dsa-2529
- https://www.djangoproject.com/weblog/2012/jul/30/security-releases-issued
- https://www.mandriva.com/security/advisories?name=MDVSA-2012:143
- https://www.openwall.com/lists/oss-security/2012/07/31/1
- https://www.openwall.com/lists/oss-security/2012/07/31/2
- https://www.ubuntu.com/usn/USN-1560-1
- http://www.debian.org/security/2012/dsa-2529
- http://www.mandriva.com/security/advisories?name=MDVSA-2012:143
- http://www.openwall.com/lists/oss-security/2012/07/31/1
- http://www.openwall.com/lists/oss-security/2012/07/31/2
- http://www.ubuntu.com/usn/USN-1560-1
