# [M] JLSEC-2026-118

## Summary
Severity: Medium
Advisory: JLSEC-2026-118
Ecosystem: Julia
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2026-04-15
Source: https://osv.dev/vulnerability/JLSEC-2026-118
Type: osv

## Affected
- Julia: `wget_jll` — affected >=0 <1.21.4+0

## Details
GNU Wget through 1.21.1 does not omit the Authorization header upon a redirect to a different origin, a related issue to CVE-2018-1000007.

## References
- https://mail.gnu.org/archive/html/bug-wget/2021-02/msg00002.html
- https://security.netapp.com/advisory/ntap-20210618-0002/
