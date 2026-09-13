# [H] JLSEC-2026-671

## Summary
Severity: High
Advisory: JLSEC-2026-671
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-671
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.7.2+0

## Details
wolfSSL before 5.4.0 allows remote attackers to cause a denial of service via DTLS because a check for return-routability can be skipped.

## References
- http://www.openwall.com/lists/oss-security/2022/08/08/6
- https://github.com/wolfSSL/wolfssl/releases/tag/v5.4.0-stable
