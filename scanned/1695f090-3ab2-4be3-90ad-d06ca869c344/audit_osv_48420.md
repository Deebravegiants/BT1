# [M] CVE-2017-7542

## Summary
Severity: Medium
Advisory: CVE-2017-7542
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-21
Source: https://osv.dev/vulnerability/CVE-2017-7542
Type: osv

## Details
The ip6_find_1stfragopt function in net/ipv6/output_core.c in the Linux kernel through 4.12.3 allows local users to cause a denial of service (integer overflow and infinite loop) by leveraging the ability to open a raw socket.

## References
- https://usn.ubuntu.com/3583-2/
- http://www.securityfocus.com/bid/99953
- https://usn.ubuntu.com/3583-1/
- https://help.ecostruxureit.com/display/public/UADCE725/Security+fixes+in+StruxureWare+Data+Center+Expert+v7.6.0
- https://access.redhat.com/errata/RHSA-2017:2918
- https://access.redhat.com/errata/RHSA-2017:2931
- http://www.debian.org/security/2017/dsa-3927
- http://www.debian.org/security/2017/dsa-3945
- https://access.redhat.com/errata/RHSA-2017:2930
- https://access.redhat.com/errata/RHSA-2018:0169
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=6399f1fae4ec29fab5ec76070435555e256ca3a6
- https://github.com/torvalds/linux/commit/6399f1fae4ec29fab5ec76070435555e256ca3a6
