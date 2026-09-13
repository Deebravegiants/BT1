# [H] Exposure of Resource to Wrong Sphere in LibreNMS

## Summary
Severity: High
Advisory: GHSA-3c33-3465-fhx2
CVE: CVE-2020-15877
CWE: CWE-668
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-08
Source: https://github.com/advisories/GHSA-3c33-3465-fhx2
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <1.65.1

## Details
An issue was discovered in LibreNMS before 1.65.1. It has insufficient access control for normal users because of "'guard' => 'admin'" instead of "'middleware' => ['can:admin']" in routes/web.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-15877
- https://github.com/librenms/librenms/pull/11915
- https://github.com/librenms/librenms/commit/e5bb6d80bc308fc56b9a01ffb76c34159995353c
- https://community.librenms.org/c/announcements
- https://github.com/librenms/librenms/compare/1.65...1.65.1
- https://github.com/librenms/librenms/releases/tag/1.65.1
- https://shielder.it/blog
