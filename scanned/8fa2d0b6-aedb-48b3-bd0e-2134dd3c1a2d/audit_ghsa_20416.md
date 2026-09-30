# [H] Deserialization of Untrusted Data in Codeigniter4

## Summary
Severity: High
Advisory: GHSA-w6jr-wj64-mc9x
CVE: CVE-2022-21647
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-w6jr-wj64-mc9x
Type: github-advisory

## Affected
- Packagist: `codeigniter4/framework` — affected >=0 <4.1.6

## Details
### Impact
Deserialization of Untrusted Data was found in the `old()` function in CodeIgniter4.
Remote attackers may inject auto-loadable arbitrary objects with this vulnerability, 
and possibly execute existing PHP code on the server.
We are aware of a working exploit, which can lead to SQL injection.

### Patches
Upgrade to v4.1.6 or later.

### Workarounds
Do not use:
- `old()` and form_helper
- `RedirectResponse::withInput()` and `redirect()->withInput()`

### References
- [PHP Object Injection | OWASP](https://owasp.org/www-community/vulnerabilities/PHP_Object_Injection)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [codeigniter4/CodeIgniter4](https://github.com/codeigniter4/CodeIgniter4/issues)
* Email us at [SECURITY.md](https://github.com/codeigniter4/CodeIgniter4/blob/develop/SECURITY.md)

## References
- https://github.com/codeigniter4/CodeIgniter4/security/advisories/GHSA-w6jr-wj64-mc9x
- https://nvd.nist.gov/vuln/detail/CVE-2022-21647
- https://github.com/codeigniter4/CodeIgniter4/commit/ce95ed5765256e2f09f3513e7d42790e0d6948f5
- https://github.com/FriendsOfPHP/security-advisories/blob/master/codeigniter4/framework/CVE-2022-21647.yaml
- https://github.com/codeigniter4/CodeIgniter4
