# [H] CVE-2021-30184

## Summary
Severity: High
Advisory: CVE-2021-30184
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-04-07
Source: https://osv.dev/vulnerability/CVE-2021-30184
Type: osv

## Details
GNU Chess 6.2.7 allows attackers to execute arbitrary code via crafted PGN (Portable Game Notation) data. This is related to a buffer overflow in the use of a .tmp.epd temporary file in the cmd_pgnload and cmd_pgnreplay functions in frontend/cmd.cc.

## References
- https://lists.debian.org/debian-lts-announce/2025/01/msg00007.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QC74RWMDLSQGV6Z3ZABNTPABB33S4YNF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SOGPLC77ZL2FACSOE5MWDS3YH3RBNQAQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XXOTMUSBVUZNA3JMPG6BU37DQW2YOJWS/
- https://security.gentoo.org/glsa/202107-28
- https://lists.gnu.org/archive/html/bug-gnu-chess/2021-04/msg00000.html
- https://lists.gnu.org/archive/html/bug-gnu-chess/2021-04/msg00001.html
