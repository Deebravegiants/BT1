# [M] LibreNMS Arbitrary File Read

## Summary
Severity: Medium
Advisory: GHSA-4ccx-wjqp-5fww
CVE: CVE-2017-16759
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4ccx-wjqp-5fww
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <1.31

## Details
The installation process in LibreNMS before 2017-08-18 allows remote attackers to read arbitrary files, related to html/install.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16759
- https://github.com/librenms/librenms/pull/7184
- https://github.com/librenms/librenms/commit/7887b2e1c7158204ac69ca43beafce66e4d3a3b4
- https://github.com/librenms/librenms/commit/d3094fa6578b29dc34fb5a7d0bd6deab49ecc911
- https://blog.librenms.org/2017/08/22/librenms-security-fix-during-the-installation-process
- https://github.com/librenms/librenms
