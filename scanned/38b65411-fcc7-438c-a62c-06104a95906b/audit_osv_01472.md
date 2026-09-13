# [H] ALPINE-CVE-2019-15847

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-15847
Ecosystem: Alpine:v3.11
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-09-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-15847
Type: osv

## Affected
- Alpine:v3.11: `gcc` — affected >=8.0 <9.3.0-r0

## Details
The POWER9 backend in GNU Compiler Collection (GCC) before version 10 could optimize multiple calls of the __builtin_darn intrinsic into a single call, thus reducing the entropy of the random number generator. This occurred because a volatile operation was not specified. For example, within a single execution of a program, the output of every __builtin_darn() call may be the same.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-15847
