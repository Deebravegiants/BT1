# [M] ALPINE-CVE-2026-26203

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-26203
Ecosystem: Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-02-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-26203
Type: osv

## Affected
- Alpine:v3.24: `pjproject` — affected >=0 <2.17-r0

## Details
PJSIP is a free and open source multimedia communication library. Versions prior to 2.17 have a critical heap buffer underflow vulnerability in PJSIP's H.264 packetizer. The bug occurs when processing malformed H.264 bitstreams without NAL unit start codes, where the packetizer performs unchecked pointer arithmetic that can read from memory located before the allocated buffer. Version 2.17 contains a patch for the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-26203
