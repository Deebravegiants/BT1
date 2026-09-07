# [H] Django vulnerable to Improper Restriction of Operations within the Bounds of a Memory Buffer

## Summary
Severity: High
Advisory: GHSA-5h2q-4hrp-v9rr
CVE: CVE-2012-3444
CWE: CWE-119
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-5h2q-4hrp-v9rr
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0 <1.3.2
- PyPI: `Django` — affected >=1.4 <1.4.1

## Details
The `get_image_dimensions` function in the image-handling functionality in Django before 1.3.2 and 1.4.x before 1.4.1 uses a constant chunk size in all attempts to determine dimensions, which allows remote attackers to cause a denial of service (process or thread consumption) via a large TIFF image.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-3444
- https://github.com/django/django/commit/9ca0ff6268eeff92d0d0ac2c315d4b6a8e229155
- https://github.com/django/django/commit/b2eb4787a0fff9c9993b78be5c698e85108f3446
- https://github.com/django/django/commit/c14f325c4eef628bc7bfd8873c3a72aeb0219141
- https://github.com/django/django/commit/da33d67181b53fe6cc737ac1220153814a1509f6
- https://github.com/django/django/commit/dd16b17099b7d86f27773df048c5014cf439b282
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2012-4.yaml
- https://www.djangoproject.com/weblog/2012/jul/30/security-releases-issued
- http://www.debian.org/security/2012/dsa-2529
- http://www.mandriva.com/security/advisories?name=MDVSA-2012:143
- http://www.openwall.com/lists/oss-security/2012/07/31/1
- http://www.openwall.com/lists/oss-security/2012/07/31/2
- http://www.ubuntu.com/usn/USN-1560-1
