# [H] CodeIgniter4 allows spoofing of IP address when using proxy

## Summary
Severity: High
Advisory: GHSA-ghw3-5qvm-3mqc
CVE: CVE-2022-23556
CWE: CWE-345
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2022-12-22
Source: https://github.com/advisories/GHSA-ghw3-5qvm-3mqc
Type: github-advisory

## Affected
- Packagist: `codeigniter4/framework` — affected >=0 <4.2.11

## Details
### Impact
This vulnerability may allow attackers to spoof their IP address when your server is behind a reverse proxy.

### Patches
Upgrade to v4.2.11 or later, and configure `Config\App::$proxyIPs`.

### Workarounds
Do not use `$request->getIPAddress()`.

### References
- https://codeigniter4.github.io/userguide/incoming/request.html#CodeIgniter\HTTP\Request::getIPAddress

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [codeigniter4/CodeIgniter4](https://github.com/codeigniter4/CodeIgniter4/issues)
* Email us at [SECURITY.md](https://github.com/codeigniter4/CodeIgniter4/blob/develop/SECURITY.md)

## References
- https://github.com/codeigniter4/CodeIgniter4/security/advisories/GHSA-ghw3-5qvm-3mqc
- https://nvd.nist.gov/vuln/detail/CVE-2022-23556
- https://github.com/codeigniter4/CodeIgniter4/commit/5ca8c99b2db09a2a08a013836628028ddc984659
- https://codeigniter4.github.io/userguide/incoming/request.html#CodeIgniter\HTTP\Request::getIPAddress
- https://github.com/FriendsOfPHP/security-advisories/blob/master/codeigniter4/framework/CVE-2022-23556.yaml
- https://github.com/codeigniter4/CodeIgniter4
