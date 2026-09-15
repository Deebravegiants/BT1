# [H] CVE-2016-2180

## Summary
Severity: High
Advisory: CVE-2016-2180
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-01
Source: https://osv.dev/vulnerability/CVE-2016-2180
Type: osv

## Details
The TS_OBJ_print_bio function in crypto/ts/ts_lib.c in the X.509 Public Key Infrastructure Time-Stamp Protocol (TSP) implementation in OpenSSL through 1.0.2h allows remote attackers to cause a denial of service (out-of-bounds read and application crash) via a crafted time-stamp file that is mishandled by the "openssl ts" command.

## References
- http://www.securitytracker.com/id/1036486
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03856en_us
- https://www.tenable.com/security/tns-2016-20
- https://www.tenable.com/security/tns-2016-21
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10759
- http://rhn.redhat.com/errata/RHSA-2016-1940.html
- http://www-01.ibm.com/support/docview.wss?uid=swg21995039
- http://www.oracle.com/technetwork/security-advisory/cpuapr2018-3678067.html
- http://www.oracle.com/technetwork/security-advisory/cpujan2018-3236628.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2017-3236622.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2016-2881722.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2017-3236626.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinoct2016-3090545.html
- http://www.oracle.com/technetwork/topics/security/ovmbulletinoct2016-3090547.html
- http://www.securityfocus.com/bid/92117
- http://www.splunk.com/view/SP-CAAAPSV
- http://www.splunk.com/view/SP-CAAAPUE
- https://bto.bluecoat.com/security-advisory/sa132
- https://kb.pulsesecure.net/articles/Pulse_Security_Advisories/SA40312
