# [M] Cross-site Scripting in LibreNMS

## Summary
Severity: Medium
Advisory: GHSA-5vr6-hm68-5j9p
CVE: CVE-2021-44279
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-12-03
Source: https://github.com/advisories/GHSA-5vr6-hm68-5j9p
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0

## Details
LibreNMS 21.11.0 is affected by is affected by a Cross Site Scripting (XSS) vulnerability in includes/html/forms/poller-groups.inc.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44279
- https://github.com/librenms/librenms/pull/13554
- https://github.com/librenms/librenms/pull/13554/commits/4f231a0f49b6c953d506913364ffd7fb3a660630
- https://github.com/librenms/librenms
