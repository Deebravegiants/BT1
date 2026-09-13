# [H] CVE-2017-11176

## Summary
Severity: High
Advisory: CVE-2017-11176
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-11
Source: https://osv.dev/vulnerability/CVE-2017-11176
Type: osv

## Details
The mq_notify function in the Linux kernel through 4.11.9 does not set the sock pointer to NULL upon entry into the retry logic. During a user-space close of a Netlink socket, it allows attackers to cause a denial of service (use-after-free) or possibly have unspecified other impact.

## References
- https://access.redhat.com/errata/RHSA-2017:2918
- https://access.redhat.com/errata/RHSA-2017:2930
- https://access.redhat.com/errata/RHSA-2017:2931
- https://access.redhat.com/errata/RHSA-2018:0169
- http://www.securityfocus.com/bid/99919
- https://access.redhat.com/errata/RHSA-2018:3822
- https://help.ecostruxureit.com/display/public/UADCE725/Security+fixes+in+StruxureWare+Data+Center+Expert+v7.6.0
- https://www.exploit-db.com/exploits/45553/
- http://www.debian.org/security/2017/dsa-3927
- http://www.debian.org/security/2017/dsa-3945
- https://github.com/torvalds/linux/commit/f991af3daabaecff34684fd51fac80319d1baad1
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=f991af3daabaecff34684fd51fac80319d1baad1
