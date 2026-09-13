# [C] Integer overflow in gawk's `builtin.c` can cause buffer overflow and denial of service

## Summary
Severity: Critical
Advisory: JLSEC-2026-786
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/JLSEC-2026-786
Type: osv

## Affected
- Julia: `gawk_jll` — affected >=0 <5.4.1+0

## Details
Integer overflow vulnerability has been found in "builtin.c" program file of gawk. This issue may lead to memory exhaustion on the hosting operating system and could be used to overwrite gawk heap metadata and objects with attacker-controlled bytes. It affects gawk in versions 5.4.0 and below.

## References
- https://cert.pl/en/posts/2026/07/CVE-2026-40467
- https://cgit.git.savannah.gnu.org/cgit/gawk.git/commit/?id=062f2f2581b991362c046f7f2e238ffa34e6f8c7
