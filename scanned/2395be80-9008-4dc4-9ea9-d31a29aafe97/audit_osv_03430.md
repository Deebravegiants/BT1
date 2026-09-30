# [H] ALPINE-CVE-2026-12064

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-12064
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-12064
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=7.81.0 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=7.81.0 <8.21.0-r0

## Details
When a user invokes curl using a schemeless URL combined with
`--proto-default` sftp (or scp), a disconnect occurs between the tool layer
and libcurl. The tool layer incorrectly infers the URL scheme, which
erroneously bypasses the initialization of critical SSH security options like
CURLOPT_SSH_HOST_PUBLIC_KEY_SHA256 and CURLOPT_SSH_KNOWNHOSTS. Conversely, the
libcurl runtime successfully honors CURLOPT_DEFAULT_PROTOCOL and establishes
the connection via SFTP/SCP as specified. Because the tool layer skipped the
security configuration, these SSH host verification options are silently
omitted, causing curl to connect to an unverified SSH remote host without
throwing an error.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-12064
