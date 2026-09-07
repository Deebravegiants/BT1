# [H] Zip slip in opencart

## Summary
Severity: High
Advisory: GHSA-m7r8-2r98-vppj
CVE: CVE-2024-21518
CWE: CWE-22, CWE-29
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-22
Source: https://github.com/advisories/GHSA-m7r8-2r98-vppj
Type: github-advisory

## Affected
- Packagist: `opencart/opencart` — affected >=4.0.0.0

## Details
This affects versions of the package opencart/opencart from 4.0.0.0. A Zip Slip issue was identified via the marketplace installer due to improper sanitization of the target path, allowing files within a malicious archive to traverse the filesystem and be extracted to arbitrary locations. An attacker can create arbitrary files in the web root of the application and overwrite other existing files by exploiting this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21518
- https://github.com/opencart/opencart
- https://github.com/opencart/opencart/blob/04c1724370ab02967d3b4f668c1b67771ecf1ff4/upload/admin/controller/marketplace/installer.php%23L383C1-L383C1
- https://security.snyk.io/vuln/SNYK-PHP-OPENCARTOPENCART-7266578
