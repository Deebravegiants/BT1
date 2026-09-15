# [H] MySQL2: Auth Plugin Downgrade to mysql_clear_password Leaks Plaintext Credentials

## Summary
Severity: High
Advisory: GHSA-3f6p-5ww8-9rcr
CWE: CWE-522
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-09-01
Source: https://github.com/advisories/GHSA-3f6p-5ww8-9rcr
Type: github-advisory

## Affected
- npm: `mysql2` — affected >=0 <3.22.0

## Details
## Summary

A rogue MySQL server (or MITM) can force mysql2 to send credentials in **plaintext** by requesting an auth switch to `mysql_clear_password`. The driver complies without verifying that TLS is active.

## Details

`mysql_clear_password` is registered as a default standard plugin in `lib/commands/auth_switch.js` (line 21). When a server sends an AuthSwitchRequest (0xFE) requesting `mysql_clear_password`, the driver executes it without checking for TLS. The plugin (`lib/auth_plugins/mysql_clear_password.js`) returns `Buffer.from(password + '\0')`.

Note: `caching_sha2_password` plugin DOES check for SSL before sending cleartext (line 77). But `mysql_clear_password` has no such guard.

## Attack Scenario

1. Attacker operates rogue MySQL server or performs MITM
2. Server advertises `caching_sha2_password` in handshake
3. Client sends hashed auth response
4. Server replies with AuthSwitchRequest to `mysql_clear_password`
5. Client sends password in plaintext
6. Attacker captures plaintext password

## PoC

Rogue MySQL server (Node.js, ~80 lines) that captures plaintext passwords from mysql2 clients. Tested against mysql2 3.20.0. Full PoC available on request.

## Suggested Fix

Remove `mysql_clear_password` from `standardAuthPlugins`, or add a guard requiring TLS/unix socket before allowing cleartext auth.

## Impact

- mysql2: 9M weekly downloads
- Any application connecting without TLS is vulnerable to credential theft
- Cloud environments with untrusted network paths are especially at risk

## References
- https://github.com/sidorares/node-mysql2/security/advisories/GHSA-3f6p-5ww8-9rcr
- https://github.com/sidorares/node-mysql2/issues/1617
- https://github.com/sidorares/node-mysql2/pull/4236
- https://github.com/sidorares/node-mysql2/commit/884bec56288d827939d0dd3f1f4ae476fbc8dbeb
- https://github.com/sidorares/node-mysql2
- https://github.com/sidorares/node-mysql2/releases/tag/v3.22.0
