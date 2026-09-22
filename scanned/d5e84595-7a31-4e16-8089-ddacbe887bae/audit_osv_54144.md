# [M] CVE-2023-4039

## Summary
Severity: Medium
Advisory: CVE-2023-4039
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2023-09-13
Source: https://osv.dev/vulnerability/CVE-2023-4039
Type: osv

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
- https://developer.arm.com/Arm%20Security%20Center/GCC%20Stack%20Protector%20Vulnerability%20AArch64
- https://github.com/metaredteam/external-disclosures/security/advisories/GHSA-x7ch-h5rf-w2mf
