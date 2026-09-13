# [H] Laravel Backpack CRUD: OS command injection in Stats::makeCurlRequest via attacker-controlled Host header (pre-auth)

## Summary
Severity: High
Advisory: GHSA-mrc5-3mm3-45c5
CVE: CVE-2026-54182
CWE: CWE-116, CWE-20, CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-mrc5-3mm3-45c5
Type: github-advisory

## Affected
- Packagist: `backpack/crud` — affected >=4.1.0 <4.1.72
- Packagist: `backpack/crud` — affected >=5.0.0 <5.6.2
- Packagist: `backpack/crud` — affected >=6.0.0 <6.8.13
- Packagist: `backpack/crud` — affected >=7.0.0 <7.0.36

## Details
## Summary

`Backpack\CRUD\Stats::makeCurlRequest` builds a shell command using unescaped input that originates from the HTTP `Host` header, then passes it to `exec()`. A specially crafted Host header can break out of the shell argument and cause the server to execute arbitrary OS commands as the web user.

The vulnerable code path is reached from `BackpackServiceProvider::boot()` on every HTTP request in production when `exec()` and `curl` are available. A 1-in-100 random gate is the only guard — an attacker can reliably trigger it by retrying.

## Severity

**High — CVSS 8.1**  
`CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H`

Attack Complexity is rated **High** because default nginx and Apache configurations typically strip or reject malformed Host headers before they reach PHP, and `exec()` is often disabled for web processes in hardened environments. Both mitigations must be absent for exploitation.

## Impact

A successful exploit yields OS command execution as the web server user (`www-data`, `nginx`, etc.), giving an unauthenticated attacker access to environment secrets (APP_KEY, database credentials, API keys in `.env`), the filesystem, and any service the server can reach.

## Fix

`makeCurlRequest` was replaced with the Guzzle-based path already present in the codebase, eliminating the shell-command construction entirely. **Upgrade to a patched release immediately.**

## Affected versions

| Branch | Vulnerable range | First safe version |
|--------|-----------------|-------------------|
| 4.1.x  | `< 4.1.70`      | 4.1.70            |
| 5.x    | `< 5.6.2`       | 5.6.2             |
| 6.x    | `< 6.8.13`      | 6.8.13            |
| 7.x    | `< 7.0.36`      | 7.0.36            |

## Credits

Reported by Vishal Shukla ([@shukla304](https://github.com/shukla304)) via sechub.dev AI Agent.

## References
- https://github.com/Laravel-Backpack/CRUD/security/advisories/GHSA-mrc5-3mm3-45c5
- https://github.com/Laravel-Backpack/CRUD
- https://github.com/Laravel-Backpack/CRUD/releases/tag/4.1.72
- https://github.com/Laravel-Backpack/CRUD/releases/tag/5.6.2
- https://github.com/Laravel-Backpack/CRUD/releases/tag/6.8.13
- https://github.com/Laravel-Backpack/CRUD/releases/tag/7.0.36
