# [M] CVE-2017-2671

## Summary
Severity: Medium
Advisory: CVE-2017-2671
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-05
Source: https://osv.dev/vulnerability/CVE-2017-2671
Type: osv

## Details
The ping_unhash function in net/ipv4/ping.c in the Linux kernel through 4.10.8 is too late in obtaining a certain lock and consequently cannot ensure that disconnect function calls are safe, which allows local users to cause a denial of service (panic) by leveraging access to the protocol value of IPPROTO_ICMP in a socket system call.

## References
- https://usn.ubuntu.com/3754-1/
- https://www.exploit-db.com/exploits/42135/
- http://openwall.com/lists/oss-security/2017/04/04/8
- http://www.securityfocus.com/bid/97407
- https://access.redhat.com/errata/RHSA-2017:2669
- https://github.com/danieljiang0415/android_kernel_crash_poc
- https://twitter.com/danieljiang0415/status/845116665184497664
- https://access.redhat.com/errata/RHSA-2017:1842
- https://access.redhat.com/errata/RHSA-2017:2077
- https://access.redhat.com/errata/RHSA-2018:1854
- https://git.kernel.org/pub/scm/linux/kernel/git/davem/net.git/commit/net/ipv4/ping.c?id=43a6684519ab0a6c52024b5e25322476cabad893
- https://github.com/torvalds/linux/commit/43a6684519ab0a6c52024b5e25322476cabad893
