# [C] Remote CLI Command Execution Vulnerability in CodeIgniter4

## Summary
Severity: Critical
Advisory: GHSA-xjp4-6w75-qrj7
CVE: CVE-2022-24711
CWE: CWE-20, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2022-03-01
Source: https://github.com/advisories/GHSA-xjp4-6w75-qrj7
Type: github-advisory

## Affected
- Packagist: `codeigniter4/framework` — affected >=0 <4.1.9

## Details
### Impact
This vulnerability allows attackers to execute CLI routes via HTTP request.

### Patches
Upgrade to v4.1.9 or later.

### Workarounds
None.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [codeigniter4/CodeIgniter4](https://github.com/codeigniter4/CodeIgniter4/issues)
* Email us at [SECURITY.md](https://github.com/codeigniter4/CodeIgniter4/blob/develop/SECURITY.md)

## References
- https://github.com/codeigniter4/CodeIgniter4/security/advisories/GHSA-xjp4-6w75-qrj7
- https://nvd.nist.gov/vuln/detail/CVE-2022-24711
- https://github.com/codeigniter4/CodeIgniter4/commit/202f41ad522ba1d414b9d9c35aba1cb0c156b781
- https://github.com/FriendsOfPHP/security-advisories/blob/master/codeigniter4/framework/CVE-2022-24711.yaml
- https://github.com/codeigniter4/CodeIgniter4
