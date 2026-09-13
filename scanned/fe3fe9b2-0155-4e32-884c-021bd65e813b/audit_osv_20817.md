# [M] CVE-2021-3740

## Summary
Severity: Medium
Advisory: CVE-2021-3740
CVSS: 6.8 (CVSS:3.1/AV:A/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-11-15
Source: https://osv.dev/vulnerability/CVE-2021-3740
Type: osv

## Details
A Session Fixation vulnerability exists in chatwoot/chatwoot versions prior to 2.4.0. The application does not invalidate existing sessions on other devices when a user changes their password, allowing old sessions to persist. This can lead to unauthorized access if an attacker has obtained a session token.

## References
- https://huntr.com/bounties/1625470476437-chatwoot/chatwoot
- https://github.com/chatwoot/chatwoot/commit/6fdd4a29969be8423f31890b807d27d13627c50c
