# [H] CVE-2017-8890

## Summary
Severity: High
Advisory: CVE-2017-8890
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-10
Source: https://osv.dev/vulnerability/CVE-2017-8890
Type: osv

## Details
The inet_csk_clone_lock function in net/ipv4/inet_connection_sock.c in the Linux kernel through 4.10.15 allows attackers to cause a denial of service (double free) or possibly have unspecified other impact by leveraging use of the accept system call.

## References
- http://www.debian.org/security/2017/dsa-3886
- https://access.redhat.com/errata/RHSA-2017:1842
- https://access.redhat.com/errata/RHSA-2017:2077
- https://access.redhat.com/errata/RHSA-2017:2669
- http://www.securityfocus.com/bid/98562
- https://access.redhat.com/errata/RHSA-2018:1854
- https://source.android.com/security/bulletin/2017-09-01
- https://github.com/torvalds/linux/commit/657831ffc38e30092a2d5f03d385d710eb88b09a
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=657831ffc38e30092a2d5f03d385d710eb88b09a
