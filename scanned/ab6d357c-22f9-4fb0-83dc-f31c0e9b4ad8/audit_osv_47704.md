# [H] CVE-2017-1000379

## Summary
Severity: High
Advisory: CVE-2017-1000379
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-19
Source: https://osv.dev/vulnerability/CVE-2017-1000379
Type: osv

## Details
The Linux Kernel running on AMD64 systems will sometimes map the contents of PIE executable, the heap or ld.so to where the stack is mapped allowing attackers to more easily manipulate the stack. Linux Kernel version 4.11.5 is affected.

## References
- http://www.securityfocus.com/bid/99284
- https://access.redhat.com/errata/RHSA-2017:1482
- https://access.redhat.com/errata/RHSA-2017:1484
- https://access.redhat.com/errata/RHSA-2017:1490
- https://access.redhat.com/errata/RHSA-2017:1647
- https://access.redhat.com/errata/RHSA-2017:1489
- https://access.redhat.com/errata/RHSA-2017:1616
- https://access.redhat.com/errata/RHSA-2017:1487
- https://access.redhat.com/errata/RHSA-2017:1491
- https://access.redhat.com/security/cve/CVE-2017-1000379
- https://www.exploit-db.com/exploits/42275/
- https://www.qualys.com/2017/06/19/stack-clash/stack-clash.txt
- https://access.redhat.com/errata/RHSA-2017:1485
- https://access.redhat.com/errata/RHSA-2017:1486
- https://access.redhat.com/errata/RHSA-2017:1488
- https://access.redhat.com/errata/RHSA-2017:1712
- https://access.redhat.com/errata/RHSA-2017:1842
