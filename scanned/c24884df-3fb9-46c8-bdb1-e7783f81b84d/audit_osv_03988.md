# [H] ALPINE-CVE-2026-9547

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-9547
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-9547
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=7.69.0 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=7.69.0 <8.21.0-r0

## Details
When a libcurl-based application performs transfers via `SCP://` or `SFTP://`
and utilizes the `CURLOPT_SSH_KEYFUNCTION` callback, it may silently accept an
untrusted server. This vulnerability occurs when a server presents a host key
type that does not match the specific key type already recorded for that host
in the `known_hosts` file. Instead of rejecting the mismatch, the callback
mechanism fails to properly enforce the restriction, allowing the connection
to succeed without warning and risking a potential man-in-the-middle attack.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-9547
