# [C] CVE-2017-12762

## Summary
Severity: Critical
Advisory: CVE-2017-12762
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-08-09
Source: https://osv.dev/vulnerability/CVE-2017-12762
Type: osv

## Details
In /drivers/isdn/i4l/isdn_net.c: A user-controlled buffer is copied into a local buffer of constant size using strcpy without a length check which can cause a buffer overflow. This affects the Linux kernel 4.9-stable tree, 4.12-stable tree, 3.18-stable tree, and 4.4-stable tree.

## References
- http://www.securityfocus.com/bid/100251
- https://usn.ubuntu.com/3620-1/
- https://usn.ubuntu.com/3620-2/
- http://www.openwall.com/lists/oss-security/2020/02/11/1
- http://www.openwall.com/lists/oss-security/2020/02/11/2
- http://www.openwall.com/lists/oss-security/2020/02/14/4
- https://patchwork.kernel.org/patch/9880041/
