# [H] CVE-2016-2181

## Summary
Severity: High
Advisory: CVE-2016-2181
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-16
Source: https://osv.dev/vulnerability/CVE-2016-2181
Type: osv

## Details
The Anti-Replay feature in the DTLS implementation in OpenSSL before 1.1.0 mishandles early use of a new epoch number in conjunction with a large sequence number, which allows remote attackers to cause a denial of service (false-positive packet drops) via spoofed DTLS records, related to rec_layer_d1.c and ssl3_record.c.

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
- http://www.securitytracker.com/id/1036690
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://git.openssl.org/?p=openssl.git%3Ba=commit%3Bh=1fb9fdc3027b27d8eb6a1e6a846435b070980770
- https://kc.mcafee.com/corporate/index?page=content&id=SB10215
- https://support.f5.com/csp/article/K59298921
- https://www.tenable.com/security/tns-2016-20
- https://www.tenable.com/security/tns-2016-21
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10759
