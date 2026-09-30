# [M] CodeIgniter Shield Vulnerable to SameSite Attackers Bypassing the CSRF Protection

## Summary
Severity: Medium
Advisory: GHSA-5hm8-vh6r-2cjq
CVE: CVE-2022-35943
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2022-08-18
Source: https://github.com/advisories/GHSA-5hm8-vh6r-2cjq
Type: github-advisory

## Affected
- Packagist: `codeigniter4/shield` — affected >=1.0.0-beta <1.0.0-beta.2

## Details
### Impact
This vulnerability may allow [SameSite Attackers](https://canitakeyoursubdomain.name/) to bypass the [CodeIgniter4 CSRF protection](https://codeigniter4.github.io/userguide/libraries/security.html) mechanism with CodeIgniter Shield.

For this attack to succeed, the attacker must have direct (or indirect, e.g., XSS) control over a subdomain site (e.g., `https://a.example.com/`) of the target site (e.g., `http://example.com/`).

This vulnerability exists whether `Config\Security::$csrfProtection` is `'cookie'` or `'session'`.
It is also exploitable whether `Config\Security::$regenerate` is `true` or `false`.

### Patches
Upgrade to **CodeIgniter v4.2.3 or later** and **Shield v1.0.0-beta.2 or later**.

### Workarounds
Do all of the following:
- set `Config\Security::$csrfProtection` to `'session'`
- remove old session data right after login (immediately after ID and password match)
- regenerate CSRF token right after login (immediately after ID and password match)

### References
- [CodeIgniter4 CSRF Protection](https://codeigniter4.github.io/userguide/libraries/security.html)
- [SameSite Attacks](https://canitakeyoursubdomain.name/)
- [SameSite Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite)
- [The great SameSite confusion](https://jub0bs.com/posts/2021-01-29-great-samesite-confusion/)

### For more information
If you have any questions or comments about this advisory:
* Open an issue or discussion in [codeigniter4/shield](https://github.com/codeigniter4/shield)
* Email us at [security@codeigniter.com](mailto:security@codeigniter.com)

## References
- https://github.com/codeigniter4/shield/security/advisories/GHSA-5hm8-vh6r-2cjq
- https://nvd.nist.gov/vuln/detail/CVE-2022-35943
- https://github.com/codeigniter4/shield/commit/342a368536678621998c3c41d276480cd14ec6c6
- https://codeigniter4.github.io/userguide/libraries/security.htm
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite
- https://github.com/codeigniter4/shield
- https://jub0bs.com/posts/2021-01-29-great-samesite-confusion
