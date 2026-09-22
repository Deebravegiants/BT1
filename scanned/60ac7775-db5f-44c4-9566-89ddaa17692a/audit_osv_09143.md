# [H] CVE-2016-8610

## Summary
Severity: High
Advisory: CVE-2016-8610
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-11-13
Source: https://osv.dev/vulnerability/CVE-2016-8610
Type: osv

## Details
A denial of service flaw was found in OpenSSL 0.9.8, 1.0.1, 1.0.2 through 1.0.2h, and 1.1.0 in the way the TLS/SSL protocol defined processing of ALERT packets during a connection handshake. A remote attacker could use this flaw to make a TLS/SSL server consume an excessive amount of CPU and fail to accept connections from other clients.

## References
- https://git.openssl.org/gitweb/?p=openssl.git%3Ba=commit%3Bh=af58be768ebb690f78530f796e92b8ae5c9a4401
- http://rhn.redhat.com/errata/RHSA-2017-0286.html
- http://rhn.redhat.com/errata/RHSA-2017-0574.html
- http://rhn.redhat.com/errata/RHSA-2017-1415.html
- http://rhn.redhat.com/errata/RHSA-2017-1659.html
- http://seclists.org/oss-sec/2016/q4/224
- http://www.securityfocus.com/bid/93841
- http://www.securitytracker.com/id/1037084
- https://access.redhat.com/errata/RHSA-2017:1413
- https://access.redhat.com/errata/RHSA-2017:1414
- https://access.redhat.com/errata/RHSA-2017:1658
- https://access.redhat.com/errata/RHSA-2017:1801
- https://access.redhat.com/errata/RHSA-2017:1802
- https://access.redhat.com/errata/RHSA-2017:2493
- https://access.redhat.com/errata/RHSA-2017:2494
- https://security.360.cn/cve/CVE-2016-8610/
- https://security.FreeBSD.org/advisories/FreeBSD-SA-16:35.openssl.asc
- https://security.netapp.com/advisory/ntap-20171130-0001/
- https://security.paloaltonetworks.com/CVE-2016-8610
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03897en_us
