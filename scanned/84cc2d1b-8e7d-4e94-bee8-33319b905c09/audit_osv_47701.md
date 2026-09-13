# [H] CVE-2017-1000365

## Summary
Severity: High
Advisory: CVE-2017-1000365
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-19
Source: https://osv.dev/vulnerability/CVE-2017-1000365
Type: osv

## Details
The Linux Kernel imposes a size restriction on the arguments and environmental strings passed through RLIMIT_STACK/RLIM_INFINITY (1/4 of the size), but does not take the argument and environment pointers into account, which allows attackers to bypass this limitation. This affects Linux Kernel versions 4.11.5 and earlier. It appears that this feature was introduced in the Linux Kernel version 2.6.23.

## References
- http://www.securityfocus.com/bid/99156
- https://access.redhat.com/security/cve/CVE-2017-1000365
- https://www.qualys.com/2017/06/19/stack-clash/stack-clash.txt
- http://www.debian.org/security/2017/dsa-3927
- http://www.debian.org/security/2017/dsa-3945
