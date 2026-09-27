# [H] CVE-2017-9074

## Summary
Severity: High
Advisory: CVE-2017-9074
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-19
Source: https://osv.dev/vulnerability/CVE-2017-9074
Type: osv

## Details
The IPv6 fragmentation implementation in the Linux kernel through 4.11.1 does not consider that the nexthdr field may be associated with an invalid option, which allows local users to cause a denial of service (out-of-bounds read and BUG) or possibly have unspecified other impact via crafted socket and send system calls.

## References
- https://access.redhat.com/errata/RHSA-2017:1842
- https://access.redhat.com/errata/RHSA-2017:2077
- https://access.redhat.com/errata/RHSA-2018:0169
- https://help.ecostruxureit.com/display/public/UADCE725/Security+fixes+in+StruxureWare+Data+Center+Expert+v7.6.0
- http://www.debian.org/security/2017/dsa-3886
- http://www.securityfocus.com/bid/98577
- https://access.redhat.com/errata/RHSA-2017:2669
- https://github.com/torvalds/linux/commit/2423496af35d94a87156b063ea5cedffc10a70a1
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=2423496af35d94a87156b063ea5cedffc10a70a1
- https://patchwork.ozlabs.org/patch/763117/
