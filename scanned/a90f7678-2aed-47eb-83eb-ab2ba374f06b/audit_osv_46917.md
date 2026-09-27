# [C] CVE-2015-8011

## Summary
Severity: Critical
Advisory: CVE-2015-8011
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-28
Source: https://osv.dev/vulnerability/CVE-2015-8011
Type: osv

## Details
Buffer overflow in the lldp_decode function in daemon/protocols/lldp.c in lldpd before 0.8.0 allows remote attackers to cause a denial of service (daemon crash) and possibly execute arbitrary code via vectors involving large management addresses and TLV boundaries.

## References
- http://www.openwall.com/lists/oss-security/2015/10/16/2
- http://www.openwall.com/lists/oss-security/2015/10/30/2
- https://github.com/vincentbernat/lldpd/commit/dd4f16e7e816f2165fba76e3d162cd8d2978dcb2
- https://lists.debian.org/debian-lts-announce/2021/02/msg00032.html
- https://us-cert.cisa.gov/ics/advisories/icsa-21-194-07
- https://www.debian.org/security/2021/dsa-4836
- http://www.openwall.com/lists/oss-security/2015/10/16/2
- http://www.openwall.com/lists/oss-security/2015/10/30/2
- https://lists.debian.org/debian-lts-announce/2021/02/msg00032.html
- http://www.openwall.com/lists/oss-security/2015/10/16/2
- http://www.openwall.com/lists/oss-security/2015/10/30/2
- https://github.com/vincentbernat/lldpd/commit/dd4f16e7e816f2165fba76e3d162cd8d2978dcb2
- https://cert-portal.siemens.com/productcert/pdf/ssa-941426.pdf
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UJ4DXFJWMZ325ECZXPZOSK7BOEDJZHPR/
