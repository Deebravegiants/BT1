# [C] Laravel Redis Horizontal Scaling Insecure Deserialization

## Summary
Severity: Critical
Advisory: GHSA-m27r-m6rx-mhm4
CVE: CVE-2026-23524
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-m27r-m6rx-mhm4
Type: github-advisory

## Affected
- Packagist: `laravel/reverb` — affected >=0 <1.7.0

## Details
### Impact

This vulnerability affects Laravel Reverb versions prior to v1.7.0 when horizontal scaling is enabled (`REVERB_SCALING_ENABLED=true`).

The exploitability of this vulnerability is increased because Redis servers are commonly deployed without authentication.

With horizontal scaling enabled, Reverb servers communicate via Redis PubSub. Reverb previously passed data from the Redis channel directly into PHP’s `unserialize()` function without restricting which classes could be instantiated.

**Risk:** Remote Code Execution (RCE)

### Patches
This vulnerability is fixed in Laravel Reverb v1.7.0.

Update your dependency to `laravel/reverb: ^1.7.0` immediately.

### Workarounds
If you cannot upgrade to v1.7.0, you should apply the following mitigations:

* Redis Security: Require a strong password for Redis access and ensure the service is only accessible via a private network or local loopback.
* Disable Scaling: If your environment uses only one Reverb node, set `REVERB_SCALING_ENABLED=false` to bypass the vulnerable logic entirely.

### Credits
This vulnerability was discovered and responsibly reported by Mohammad Yaser Abo-Elmaaty @m0h4mmad

## References
- https://github.com/laravel/reverb/security/advisories/GHSA-m27r-m6rx-mhm4
- https://nvd.nist.gov/vuln/detail/CVE-2026-23524
- https://github.com/laravel/reverb/commit/9ec26f8ffbb701f84920dd0bb9781a1797591f1a
- https://github.com/laravel/reverb
- https://github.com/laravel/reverb/releases/tag/v1.7.0
- https://laravel.com/docs/12.x/reverb#scaling
- https://laravel.com/docs/reverb#scaling
