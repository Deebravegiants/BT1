# [H] CVE-2018-18653

## Summary
Severity: High
Advisory: CVE-2018-18653
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-26
Source: https://osv.dev/vulnerability/CVE-2018-18653
Type: osv

## Details
The Linux kernel, as used in Ubuntu 18.10 and when booted with UEFI Secure Boot enabled, allows privileged local users to bypass intended Secure Boot restrictions and execute untrusted code by loading arbitrary kernel modules. This occurs because a modified kernel/module.c, in conjunction with certain configuration options, leads to mishandling of the result of signature verification.

## References
- https://launchpad.net/bugs/1798863
- https://usn.ubuntu.com/3832-1/
- https://usn.ubuntu.com/3835-1/
