# [C] ALPINE-CVE-2026-27820

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-27820
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-27820
Type: osv

## Affected
- Alpine:v3.23: `ruby` — affected >=0 <3.4.9-r0
- Alpine:v3.24: `ruby` — affected >=0 <3.4.9-r0

## Details
zlib is a Ruby interface for the zlib compression/decompression library. Versions 3.0.0 and below, 3.1.0, 3.1.1, 3.2.0 and 3.2.1 contain a buffer overflow vulnerability in the Zlib::GzipReader. The zstream_buffer_ungets function prepends caller-provided bytes ahead of previously produced output but fails to guarantee the backing Ruby string has enough capacity before the memmove shifts the existing data. This can lead to memory corruption when the buffer length exceeds capacity. This issue has been fixed in versions 3.0.1, 3.1.2 and 3.2.3.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-27820
