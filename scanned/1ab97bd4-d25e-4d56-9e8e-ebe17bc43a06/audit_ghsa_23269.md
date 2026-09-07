# [H] Dolibarr authenticated Remote Code Execution

## Summary
Severity: High
Advisory: GHSA-7x8g-h246-gvx3
CVE: CVE-2020-35136
CWE: CWE-77, CWE-88
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7x8g-h246-gvx3
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <12.0.4

## Details
Dolibarr 12.0.3 is vulnerable to authenticated Remote Code Execution. An attacker who has the access the admin dashboard can manipulate the backup function by inserting a payload into the filename for the zipfilename_template parameter to admin/tools/dolibarr_export.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35136
- https://github.com/Dolibarr/dolibarr/commit/4fcd3fe49332baab0e424225ad10b76b47ebcbac
- https://github.com/Dolibarr/dolibarr
- https://github.com/Dolibarr/dolibarr/releases
- https://sourceforge.net/projects/dolibarr
- http://bilishim.com/2020/12/18/zero-hunting-2.html
