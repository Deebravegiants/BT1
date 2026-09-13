# [C] JLSEC-2026-120

## Summary
Severity: Critical
Advisory: JLSEC-2026-120
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-04-15
Source: https://osv.dev/vulnerability/JLSEC-2026-120
Type: osv

## Affected
- Julia: `wget_jll` — affected >=0 <1.25.0+0

## Details
url.c in GNU Wget through 1.24.5 mishandles semicolons in the userinfo subcomponent of a URI, and thus there may be insecure behavior in which data that was supposed to be in the userinfo subcomponent is misinterpreted to be part of the host subcomponent.

## References
- https://git.savannah.gnu.org/cgit/wget.git/commit/?id=ed0c7c7e0e8f7298352646b2fd6e06a11e242ace
- https://lists.debian.org/debian-lts-announce/2025/04/msg00029.html
- https://lists.gnu.org/archive/html/bug-wget/2024-06/msg00005.html
- https://security.netapp.com/advisory/ntap-20241115-0005/
