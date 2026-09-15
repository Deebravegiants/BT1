# [H] ALPINE-CVE-2022-41318

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-41318
Ecosystem: Alpine:v3.15, Alpine:v3.16
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2022-12-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-41318
Type: osv

## Affected
- Alpine:v3.15: `squid` — affected >=2.5 <5.2-r1
- Alpine:v3.16: `squid` — affected >=2.5 <5.2-r1

## Details
A buffer over-read was discovered in libntlmauth in Squid 2.5 through 5.6. Due to incorrect integer-overflow protection, the SSPI and SMB authentication helpers are vulnerable to reading unintended memory locations. In some configurations, cleartext credentials from these locations are sent to a client. This is fixed in 5.7.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-41318
