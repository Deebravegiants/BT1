# [M] A flaw was found in libxml2

## Summary
Severity: Medium
Advisory: JLSEC-2025-73
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-17
Source: https://osv.dev/vulnerability/JLSEC-2025-73
Type: osv

## Affected
- Julia: `XML2_jll` — affected >=0 <2.9.12+0

## Details
A flaw was found in libxml2. Exponential entity expansion attack its possible bypassing all existing protection mechanisms and leading to denial of service.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1950515
- https://security.netapp.com/advisory/ntap-20210805-0007/
- https://www.oracle.com/security-alerts/cpujan2022.html
