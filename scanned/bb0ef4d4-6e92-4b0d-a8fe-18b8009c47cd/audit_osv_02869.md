# [M] ALPINE-CVE-2023-4039

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-4039
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2023-09-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-4039
Type: osv

## Affected
- Alpine:v3.19: `gcc` — affected >=0 <13.2.1_git20231014-r0
- Alpine:v3.20: `gcc` — affected >=0 <13.2.1_git20231014-r0
- Alpine:v3.21: `gcc` — affected >=0 <13.2.1_git20231014-r0
- Alpine:v3.22: `gcc` — affected >=0 <13.2.1_git20231014-r0
- Alpine:v3.23: `gcc` — affected >=0 <13.2.1_git20231014-r0
- Alpine:v3.24: `gcc` — affected >=0 <13.2.1_git20231014-r0

## Details
**DISPUTED**A failure in the -fstack-protector feature in GCC-based toolchains 
that target AArch64 allows an attacker to exploit an existing buffer 
overflow in dynamically-sized local variables in your application 
without this being detected. This stack-protector failure only applies 
to C99-style dynamically-sized local variables or those created using 
alloca(). The stack-protector operates as intended for statically-sized 
local variables.

The default behavior when the stack-protector 
detects an overflow is to terminate your application, resulting in 
controlled loss of availability. An attacker who can exploit a buffer 
overflow without triggering the stack-protector might be able to change 
program flow control to cause an uncontrolled loss of availability or to
 go further and affect confidentiality or integrity. NOTE: The GCC project argues that this is a missed hardening bug and not a vulnerability by itself.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-4039
