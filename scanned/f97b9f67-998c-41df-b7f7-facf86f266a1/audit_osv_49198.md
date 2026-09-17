# [H] CVE-2018-5390

## Summary
Severity: High
Advisory: CVE-2018-5390
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-06
Source: https://osv.dev/vulnerability/CVE-2018-5390
Type: osv

## Details
Linux kernel versions 4.9+ can be forced to make very expensive calls to tcp_collapse_ofo_queue() and tcp_prune_ofo_queue() for every incoming packet which can lead to a denial of service.

## References
- https://support.f5.com/csp/article/K95343321?utm_source=f5support&amp%3Butm_medium=RSS
- http://www.securityfocus.com/bid/104976
- https://access.redhat.com/errata/RHSA-2018:2384
- https://access.redhat.com/errata/RHSA-2018:2645
- https://access.redhat.com/errata/RHSA-2018:2789
- https://lists.debian.org/debian-lts-announce/2018/08/msg00014.html
- https://help.ecostruxureit.com/display/public/UADCE725/Security+fixes+in+StruxureWare+Data+Center+Expert+v7.6.0
- https://support.f5.com/csp/article/K95343321
- https://www.synology.com/support/security/Synology_SA_18_41
- http://www.openwall.com/lists/oss-security/2019/06/28/2
- https://access.redhat.com/errata/RHSA-2018:2403
- https://access.redhat.com/errata/RHSA-2018:2791
- https://access.redhat.com/errata/RHSA-2018:2933
- https://usn.ubuntu.com/3742-2/
- https://www.a10networks.com/support/security-advisories/tcp-ip-cve-2018-5390-segmentsmack
- http://www.arubanetworks.com/assets/alert/ARUBA-PSA-2018-004.txt
- http://www.openwall.com/lists/oss-security/2019/07/06/3
- https://cert-portal.siemens.com/productcert/pdf/ssa-377115.pdf
- https://usn.ubuntu.com/3732-2/
- https://www.oracle.com/security-alerts/cpujul2020.html
