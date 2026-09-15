# [H] Buffer overflow in gawk's `readdir.c` can cause denial of service and possible code execution

## Summary
Severity: High
Advisory: JLSEC-2026-788
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/JLSEC-2026-788
Type: osv

## Affected
- Julia: `gawk_jll` — affected >=0 <5.4.1+0

## Details
Buffer overflow vulnerability has been found in "`extension/readdir.c`" program file of gawk (ftype() routine). This issue could be used to crash the program and potentially to achieve code execution, although the latter has not been confirmed to be feasible. It affects gawk in versions 5.4.0 and below.

## References
- https://cert.pl/en/posts/2026/07/CVE-2026-40467
- https://cgit.git.savannah.gnu.org/cgit/gawk.git/commit/?id=cca0366144336b49aaa7d5d949966ce8e2c70843
