# [H] CodeIgniter4 Potential Session Handlers Vulnerability

## Summary
Severity: High
Advisory: GHSA-6cq5-8cj7-g558
CVE: CVE-2022-46170
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2022-12-22
Source: https://github.com/advisories/GHSA-6cq5-8cj7-g558
Type: github-advisory

## Affected
- Packagist: `codeigniter4/framework` — affected >=0 <4.2.11

## Details
### Impact
When an application uses (1) multiple session cookies (e.g., one for user pages and one for admin pages) and (2)  a session handler is set to `DatabaseHandler`, `MemcachedHandler`, or `RedisHandler`, then if an attacker gets one session cookie (e.g., one for user pages), they may be able to access pages that require another session cookie (e.g., for admin pages).

### Patches
Upgrade to version 4.2.11 or later.

### Workarounds
- Use only one session cookie.

### References
- https://codeigniter4.github.io/userguide/libraries/sessions.html#session-drivers

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [codeigniter4/CodeIgniter4](https://github.com/codeigniter4/CodeIgniter4/issues)
* Email us at [SECURITY.md](https://github.com/codeigniter4/CodeIgniter4/blob/develop/SECURITY.md)

## References
- https://github.com/codeigniter4/CodeIgniter4/security/advisories/GHSA-6cq5-8cj7-g558
- https://nvd.nist.gov/vuln/detail/CVE-2022-46170
- https://github.com/codeigniter4/CodeIgniter4/commit/f9fb6574fbeb5a4aa63f7ea87296523e10db9328
- https://codeigniter4.github.io/userguide/libraries/sessions.html#session-drivers
- https://github.com/FriendsOfPHP/security-advisories/blob/master/codeigniter4/framework/CVE-2022-46170.yaml
- https://github.com/codeigniter4/CodeIgniter4
