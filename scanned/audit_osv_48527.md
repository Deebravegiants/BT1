# [H] CVE-2017-9075

## Summary
Severity: High
Advisory: CVE-2017-9075
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-19
Source: https://osv.dev/vulnerability/CVE-2017-9075
Type: osv

## Details
The sctp_v6_create_accept_sk function in net/sctp/ipv6.c in the Linux kernel through 4.11.1 mishandles inheritance, which allows local users to cause a denial of service or possibly have unspecified other impact via crafted system calls, a related issue to CVE-2017-8890.

## References
- https://access.redhat.com/errata/RHSA-2017:1842
- https://access.redhat.com/errata/RHSA-2017:2077
- https://access.redhat.com/errata/RHSA-2018:1854
- https://source.android.com/security/bulletin/2017-10-01
- http://www.debian.org/security/2017/dsa-3886
- http://www.securityfocus.com/bid/98597
- https://access.redhat.com/errata/RHSA-2017:2669
- https://github.com/torvalds/linux/commit/fdcee2cbb8438702ea1b328fb6e0ac5e9a40c7f8
- https://patchwork.ozlabs.org/patch/763569/
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=fdcee2cbb8438702ea1b328fb6e0ac5e9a40c7f8
