# [H] ALPINE-CVE-2026-34714

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-34714
Ecosystem: Alpine:v3.23
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-34714
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=9.1.1390 <9.2.0272-r0

## Details
Vim before 9.2.0272 allows code execution that happens immediately upon opening a crafted file in the default configuration, because %{expr} injection occurs with tabpanel lacking P_MLE.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-34714
