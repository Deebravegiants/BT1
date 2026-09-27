# [C] ALPINE-CVE-2026-34582

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-34582
Ecosystem: Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-34582
Type: osv

## Affected
- Alpine:v3.24: `botan3` — affected >=0 <3.11.1-r0

## Details
Botan is a C++ cryptography library. Prior to version 3.11.1, the TLS 1.3 implementation allowed ApplicationData records to be processed prior to the Finished message being received. A server which is attempting to enforce client authentication via certificates can by bypassed by a client which entirely omits Certificate, CertificateVerify, and the Finished message and instead sends application data records. This vulnerability is fixed in 3.11.1.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-34582
