# [H] CodeIgniter4 vulnerable to information disclosure when detailed error report is displayed in production environment 

## Summary
Severity: High
Advisory: GHSA-hwxf-qxj7-7rfj
CVE: CVE-2023-46240
CWE: CWE-209
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-10-30
Source: https://github.com/advisories/GHSA-hwxf-qxj7-7rfj
Type: github-advisory

## Affected
- Packagist: `codeigniter4/framework` — affected >=0 <4.4.3

## Details
### Impact
If an error or exception occurs in CodeIgniter4 v4.4.2 and earlier, a detailed error report is displayed even if in the production environment. As a result, confidential information may be leaked.

### Patches
Upgrade to v4.4.3 or later. See [upgrading guide](https://codeigniter4.github.io/userguide/installation/upgrade_443.html).

### Workarounds
Replace `ini_set('display_errors', '0')` with `ini_set('display_errors', 'Off')` in `app/Config/Boot/production.php`.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [codeigniter4/CodeIgniter4](https://github.com/codeigniter4/CodeIgniter4/issues)
* Email us at [SECURITY.md](https://github.com/codeigniter4/CodeIgniter4/blob/develop/SECURITY.md)

## References
- https://github.com/codeigniter4/CodeIgniter4/security/advisories/GHSA-hwxf-qxj7-7rfj
- https://nvd.nist.gov/vuln/detail/CVE-2023-46240
- https://github.com/codeigniter4/CodeIgniter4/commit/423569fc31e29f51635a2e59c89770333f0e7563
- https://codeigniter4.github.io/userguide/general/errors.html#error-reporting
- https://github.com/codeigniter4/CodeIgniter4
