# [H] ALPINE-CVE-2025-30189

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-30189
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-10-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-30189
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=0 <2.4.2-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.4.2-r0

## Details
When cache is enabled, some passdb/userdb drivers incorrectly cache all users with same cache key, causing wrong cached information to be used for these users. After cached login, all subsequent logins are for same user. Install fixed version or disable caching either globally or for the impacted passdb/userdb drivers. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-30189
