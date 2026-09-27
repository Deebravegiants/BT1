# [H] CVE-2017-1000364

## Summary
Severity: High
Advisory: CVE-2017-1000364
CVSS: 7.4 (CVSS:3.0/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-19
Source: https://osv.dev/vulnerability/CVE-2017-1000364
Type: osv

## Details
An issue was discovered in the size of the stack guard page on Linux, specifically a 4k stack guard page is not sufficiently large and can be "jumped" over (the stack guard page is bypassed), this affects Linux Kernel versions 4.11.5 and earlier (the stackguard page was introduced in 2010).

## References
- https://kc.mcafee.com/corporate/index?page=content&id=SB10205
- https://www.exploit-db.com/exploits/45625/
- http://www.securitytracker.com/id/1038724
- https://kc.mcafee.com/corporate/index?page=content&id=SB10207
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03800en_us
- https://access.redhat.com/errata/RHSA-2017:1486
- https://access.redhat.com/errata/RHSA-2017:1490
- https://access.redhat.com/errata/RHSA-2017:1567
- http://www.debian.org/security/2017/dsa-3886
- https://access.redhat.com/errata/RHSA-2017:1483
- https://access.redhat.com/errata/RHSA-2017:1489
- https://access.redhat.com/errata/RHSA-2017:1647
- https://www.suse.com/security/cve/CVE-2017-1000364/
- https://access.redhat.com/errata/RHSA-2017:1482
- https://access.redhat.com/errata/RHSA-2017:1484
- https://access.redhat.com/errata/RHSA-2017:1487
- https://access.redhat.com/errata/RHSA-2017:1488
- https://www.qualys.com/2017/06/19/stack-clash/stack-clash.txt
- https://access.redhat.com/errata/RHSA-2017:1491
- https://access.redhat.com/errata/RHSA-2017:1616
