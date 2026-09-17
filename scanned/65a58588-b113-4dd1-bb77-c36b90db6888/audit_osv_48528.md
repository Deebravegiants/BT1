# [H] CVE-2017-9076

## Summary
Severity: High
Advisory: CVE-2017-9076
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-19
Source: https://osv.dev/vulnerability/CVE-2017-9076
Type: osv

## Details
The dccp_v6_request_recv_sock function in net/dccp/ipv6.c in the Linux kernel through 4.11.1 mishandles inheritance, which allows local users to cause a denial of service or possibly have unspecified other impact via crafted system calls, a related issue to CVE-2017-8890.

## References
- https://access.redhat.com/errata/RHSA-2017:2077
- https://access.redhat.com/errata/RHSA-2018:1854
- https://source.android.com/security/bulletin/2017-09-01
- http://www.debian.org/security/2017/dsa-3886
- https://access.redhat.com/errata/RHSA-2017:2669
- http://www.securityfocus.com/bid/98586
- https://access.redhat.com/errata/RHSA-2017:1842
- https://github.com/torvalds/linux/commit/83eaddab4378db256d00d295bda6ca997cd13a52
- https://patchwork.ozlabs.org/patch/760370/
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=83eaddab4378db256d00d295bda6ca997cd13a52
