# [H] CVE-2016-5195

## Summary
Severity: High
Advisory: CVE-2016-5195
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-11-10
Source: https://osv.dev/vulnerability/CVE-2016-5195
Type: osv

## Details
Race condition in mm/gup.c in the Linux kernel 2.x through 4.x before 4.8.3 allows local users to gain privileges by leveraging incorrect handling of a copy-on-write (COW) feature to write to a read-only memory mapping, as exploited in the wild in October 2016, aka "Dirty COW."

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2016-5195
- http://seclists.org/fulldisclosure/2024/Aug/35
- http://rhn.redhat.com/errata/RHSA-2016-2133.html
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-c05352241
- http://www.openwall.com/lists/oss-security/2016/10/30/1
- http://www.ubuntu.com/usn/USN-3107-1
- https://access.redhat.com/errata/RHSA-2017:0372
- https://dirtycow.ninja
- https://kc.mcafee.com/corporate/index?page=content&id=SB10177
- https://www.arista.com/en/support/advisories-notices/security-advisories/1753-security-advisory-0026
- http://rhn.redhat.com/errata/RHSA-2016-2106.html
- https://security.netapp.com/advisory/ntap-20161025-0001/
- http://packetstormsecurity.com/files/142151/Kernel-Live-Patch-Security-Notice-LSN-0021-1.html
- http://www.ubuntu.com/usn/USN-3106-4
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbgn03707en_us
- http://www.securityfocus.com/archive/1/540252/100/0/threaded
- http://www.securityfocus.com/bid/93793
- https://help.ecostruxureit.com/display/public/UADCO8x/StruxureWare+Data+Center+Operation+Software+Vulnerability+Fixes
- http://www.openwall.com/lists/oss-security/2016/10/27/13
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbgn03722en_us
