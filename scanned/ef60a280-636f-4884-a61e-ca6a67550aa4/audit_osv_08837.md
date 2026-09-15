# [H] CVE-2016-6302

## Summary
Severity: High
Advisory: CVE-2016-6302
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-16
Source: https://osv.dev/vulnerability/CVE-2016-6302
Type: osv

## Details
The tls_decrypt_ticket function in ssl/t1_lib.c in OpenSSL before 1.1.0 does not consider the HMAC size during validation of the ticket length, which allows remote attackers to cause a denial of service via a ticket that is too short.

## References
- http://www.securitytracker.com/id/1036885
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://git.openssl.org/?p=openssl.git%3Ba=commit%3Bh=e97763c92c655dcf4af2860b3abd2bc4c8a267f9
- https://www.tenable.com/security/tns-2016-20
- https://www.tenable.com/security/tns-2016-21
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10759
- http://rhn.redhat.com/errata/RHSA-2016-1940.html
- http://www-01.ibm.com/support/docview.wss?uid=swg21995039
- http://www.oracle.com/technetwork/security-advisory/cpuapr2018-3678067.html
- http://www.oracle.com/technetwork/security-advisory/cpujan2018-3236628.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2017-3236622.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2017-3236626.html
- http://www.securityfocus.com/bid/92628
- http://www.splunk.com/view/SP-CAAAPSV
- http://www.splunk.com/view/SP-CAAAPUE
- https://access.redhat.com/errata/RHSA-2018:2185
- https://access.redhat.com/errata/RHSA-2018:2186
- https://access.redhat.com/errata/RHSA-2018:2187
- https://bto.bluecoat.com/security-advisory/sa132
- https://kb.pulsesecure.net/articles/Pulse_Security_Advisories/SA40312
