# [H] Arbitrary File Creation in opencart

## Summary
Severity: High
Advisory: GHSA-7q3h-j95q-3vjh
CVE: CVE-2024-21519
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-22
Source: https://github.com/advisories/GHSA-7q3h-j95q-3vjh
Type: github-advisory

## Affected
- Packagist: `opencart/opencart` — affected >=4.0.0.0

## Details
This affects versions of the package opencart/opencart from 4.0.0.0. An Arbitrary File Creation issue was identified via the database restoration functionality. By injecting PHP code into the database, an attacker with admin privileges can create a backup file with an arbitrary filename (including the extension), within /system/storage/backup.

**Note:**

It is less likely for the created file to be available within the web root, as part of the security recommendations for the application suggest moving the storage path outside of the web root.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21519
- https://github.com/opencart/opencart
- https://github.com/opencart/opencart/blob/4.0.2.3/upload/admin/controller/tool/upload.php%23L353
- https://github.com/opencart/opencart/blob/master/upload/admin/controller/tool/upload.php%23L353
- https://security.snyk.io/vuln/SNYK-PHP-OPENCARTOPENCART-7266579
