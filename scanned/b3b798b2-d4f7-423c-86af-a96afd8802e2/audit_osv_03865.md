# [H] ALPINE-CVE-2026-5773

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-5773
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-5773
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=7.40.0 <8.20.0-r0
- Alpine:v3.24: `curl` — affected >=7.40.0 <8.20.0-r0

## Details
libcurl might in some circumstances reuse the wrong connection for SMB(S)
transfers.

libcurl features a pool of recent connections so that subsequent requests can
reuse an existing connection to avoid overhead.

When reusing a connection a range of criteria must be met. Due to a logical
error in the code, a network transfer operation that was requested by an
application could wrongfully reuse an existing SMB connection to the same
server that was using a different 'share' than the new subsequent transfer
should.

This could in unlucky situations lead to the download of the wrong file or the
upload of a file to the wrong place. When this happens, the same credentials
are used and the server name is the same.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-5773
