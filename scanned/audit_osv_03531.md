# [M] ALPINE-CVE-2026-26967

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-26967
Ecosystem: Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-02-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-26967
Type: osv

## Affected
- Alpine:v3.24: `pjproject` — affected >=0 <2.17-r0

## Details
PJSIP is a free and open source multimedia communication library written in C. In versions 2.16 and below, there is a critical Heap-based Buffer Overflow vulnerability in PJSIP's H.264 unpacketizer. The bug occurs when processing malformed SRTP packets, where the unpacketizer reads a 2-byte NAL unit size field without validating that both bytes are within the payload buffer bounds. The vulnerability affects applications that receive video using H.264. A patch is available at https://github.com/pjsip/pjproject/commit/f821c214e52b11bae11e4cd3c7f0864538fb5491.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-26967
