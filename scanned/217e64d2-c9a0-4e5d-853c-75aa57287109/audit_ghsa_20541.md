# [M] Cross-site Scripting Vulnerability in CodeIgniter4

## Summary
Severity: Medium
Advisory: GHSA-7528-7jg5-6g62
CVE: CVE-2022-21715
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-01-27
Source: https://github.com/advisories/GHSA-7528-7jg5-6g62
Type: github-advisory

## Affected
- Packagist: `codeigniter4/framework` — affected >=0 <4.1.8

## Details
### Impact
Cross-Site Scripting (XSS) vulnerability was found in `API\ResponseTrait` in Codeigniter4.
Attackers can do XSS attacks if you are using `API\ResponseTrait`.

### Patches
Upgrade to v4.1.8 or later.

### Workarounds
Do one of the following:
1. Do not use `API\ResponseTrait` nor `ResourceController`
2. Disable Auto Route and [Use Defined Routes Only](https://codeigniter4.github.io/userguide/incoming/routing.html#use-defined-routes-only)

### References
- [Cross Site Scripting (XSS) Software Attack | OWASP Foundation](https://owasp.org/www-community/attacks/xss/)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [codeigniter4/CodeIgniter4](https://github.com/codeigniter4/CodeIgniter4/issues)
* Email us at [SECURITY.md](https://github.com/codeigniter4/CodeIgniter4/blob/develop/SECURITY.md)

## References
- https://github.com/codeigniter4/CodeIgniter4/security/advisories/GHSA-7528-7jg5-6g62
- https://nvd.nist.gov/vuln/detail/CVE-2022-21715
- https://github.com/codeigniter4/CodeIgniter4/commit/70d881cf5322b7c32e69516aebd2273ac6a1e8dd
- https://codeigniter4.github.io/userguide/incoming/routing.html#use-defined-routes-only
- https://github.com/FriendsOfPHP/security-advisories/blob/master/codeigniter4/framework/CVE-2022-21715.yaml
- https://github.com/codeigniter4/framework
