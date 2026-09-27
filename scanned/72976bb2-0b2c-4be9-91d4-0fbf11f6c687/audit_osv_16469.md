# [H] CVE-2019-7303

## Summary
Severity: High
Advisory: CVE-2019-7303
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-04-23
Source: https://osv.dev/vulnerability/CVE-2019-7303
Type: osv

## Details
A vulnerability in the seccomp filters of Canonical snapd before version 2.37.4 allows a strict mode snap to insert characters into a terminal on a 64-bit host. The seccomp rules were generated to match 64-bit ioctl(2) commands on a 64-bit platform; however, the Linux kernel only uses the lower 32 bits to determine which ioctl(2) commands to run. This issue affects: Canonical snapd versions prior to 2.37.4.

## References
- https://usn.ubuntu.com/3917-1/
- https://www.exploit-db.com/exploits/46594
