# [C] VaulTLS has a password-based login exploit in additional user accounts

## Summary
Severity: Critical
Advisory: CVE-2025-55299
Aliases: GHSA-pjfr-pj3h-cw8m
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2025-08-18
Source: https://osv.dev/vulnerability/CVE-2025-55299
Type: osv

## Details
VaulTLS is a modern solution for managing mTLS (mutual TLS) certificates. Prior to 0.9.1, user accounts created through the User web UI have an empty but not NULL password set, attackers can use this to login with an empty password. This is combined with that fact, that previously disabling the password based login only effected the frontend, but still allowed login via the API. This vulnerability is fixed in 0.9.1.

## References
- https://github.com/7ritn/VaulTLS/security/advisories/GHSA-pjfr-pj3h-cw8m
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55299.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-55299
- https://github.com/7ritn/VaulTLS/commit/6ac0a43a768f1753f6889ba43f914e773a4b45c0
