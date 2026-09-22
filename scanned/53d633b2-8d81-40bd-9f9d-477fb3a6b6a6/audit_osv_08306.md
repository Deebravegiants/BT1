# [C] CVE-2016-2177

## Summary
Severity: Critical
Advisory: CVE-2016-2177
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-06-20
Source: https://osv.dev/vulnerability/CVE-2016-2177
Type: osv

## Details
OpenSSL through 1.0.2h incorrectly uses pointer arithmetic for heap-buffer boundary checks, which might allow remote attackers to cause a denial of service (integer overflow and application crash) or possibly have unspecified other impact by leveraging unexpected malloc behavior, related to s3_srvr.c, ssl_sess.c, and t1_lib.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-09/msg00022.html
- http://lists.opensuse.org/opensuse-security-announce/2016-09/msg00023.html
- http://lists.opensuse.org/opensuse-security-announce/2016-09/msg00024.html
- http://lists.opensuse.org/opensuse-security-announce/2016-09/msg00031.html
- http://lists.opensuse.org/opensuse-security-announce/2016-10/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2016-10/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2016-10/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2016-10/msg00029.html
- http://lists.opensuse.org/opensuse-security-announce/2017-10/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2017-10/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2018-02/msg00032.html
- http://seclists.org/fulldisclosure/2017/Jul/31
- http://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20160927-openssl
- http://www.openwall.com/lists/oss-security/2016/06/08/9
- http://www.securityfocus.com/archive/1/540957/100/0/threaded
- http://www.securityfocus.com/archive/1/archive/1/540957/100/0/threaded
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://git.openssl.org/?p=openssl.git%3Ba=commit%3Bh=a004e72b95835136d3f1ea90517f706c24c03da7
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-c05302448
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03763en_us
