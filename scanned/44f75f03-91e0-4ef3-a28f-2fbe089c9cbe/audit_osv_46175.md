# [M] JLSEC-2026-763

## Summary
Severity: Medium
Advisory: JLSEC-2026-763
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/JLSEC-2026-763
Type: osv

## Affected
- Julia: `iperf_jll` — affected >=0 <3.21.0+0

## Details
In iperf before 3.19.1, `iperf_auth.c` has a Base64Decode assertion failure and application exit upon a malformed authentication attempt.

## References
- https://github.com/esnet/iperf/commit/4eab661da0bbaac04493fa40164e928c6df7934a
- https://github.com/esnet/iperf/releases/tag/3.19.1
- https://lists.debian.org/debian-lts-announce/2025/08/msg00020.html
