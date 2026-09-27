# [H] CVE-2017-8824

## Summary
Severity: High
Advisory: CVE-2017-8824
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-05
Source: https://osv.dev/vulnerability/CVE-2017-8824
Type: osv

## Details
The dccp_disconnect function in net/dccp/proto.c in the Linux kernel through 4.14.3 allows local users to gain privileges or cause a denial of service (use-after-free) via an AF_UNSPEC connect system call during the DCCP_LISTEN state.

## References
- https://usn.ubuntu.com/3581-1/
- https://www.debian.org/security/2018/dsa-4082
- http://lists.opensuse.org/opensuse-security-announce/2018-01/msg00007.html
- https://access.redhat.com/errata/RHSA-2018:1170
- https://access.redhat.com/errata/RHSA-2018:3822
- https://usn.ubuntu.com/3581-2/
- https://usn.ubuntu.com/3581-3/
- https://usn.ubuntu.com/3583-1/
- https://usn.ubuntu.com/3583-2/
- http://www.openwall.com/lists/oss-security/2017/12/05/1
- https://access.redhat.com/errata/RHSA-2018:0399
- https://access.redhat.com/errata/RHSA-2018:1062
- https://access.redhat.com/errata/RHSA-2018:1130
- https://usn.ubuntu.com/3582-2/
- https://www.debian.org/security/2017/dsa-4073
- http://lists.openwall.net/netdev/2017/12/04/224
- https://access.redhat.com/errata/RHSA-2018:0676
- https://access.redhat.com/errata/RHSA-2018:1216
- https://access.redhat.com/errata/RHSA-2018:1319
- https://help.ecostruxureit.com/display/public/UADCE725/Security+fixes+in+StruxureWare+Data+Center+Expert+v7.6.0
