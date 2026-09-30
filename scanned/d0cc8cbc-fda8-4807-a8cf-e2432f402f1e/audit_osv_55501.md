# [M] CVE-2025-59777

## Summary
Severity: Medium
Advisory: CVE-2025-59777
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2025-11-10
Source: https://osv.dev/vulnerability/CVE-2025-59777
Type: osv

## Details
NULL pointer dereference vulnerability exists in GNU libmicrohttpd v1.0.2 and earlier. The vulnerability was fixed in commit ff13abc on the master branch of the libmicrohttpd Git repository, after the v1.0.2 tag. A specially crafted packet sent by an attacker could cause a denial-of-service (DoS) condition.

## References
- https://www.gnu.org/software/libmicrohttpd/
- https://jvn.jp/en/jp/JVN76719218/
- https://git.gnunet.org/libmicrohttpd.git/commit/?id=ff13abc1c1d7d2b30d69d5c0bd4a237e1801c50b
