# [M] CVE-2020-8832

## Summary
Severity: Medium
Advisory: CVE-2020-8832
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-04-10
Source: https://osv.dev/vulnerability/CVE-2020-8832
Type: osv

## Details
The fix for the Linux kernel in Ubuntu 18.04 LTS for CVE-2019-14615 ("The Linux kernel did not properly clear data structures on context switches for certain Intel graphics processors.") was discovered to be incomplete, meaning that in versions of the kernel before 4.15.0-91.92, an attacker could use this vulnerability to expose sensitive information.

## References
- https://security.netapp.com/advisory/ntap-20200430-0004/
- https://usn.ubuntu.com/usn/usn-4302-1
- https://bugs.launchpad.net/ubuntu/+source/linux/+bug/1862840
