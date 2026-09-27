# [M] CVE-2016-6512

## Summary
Severity: Medium
Advisory: CVE-2016-6512
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-06
Source: https://osv.dev/vulnerability/CVE-2016-6512
Type: osv

## Details
epan/dissectors/packet-wap.c in Wireshark 2.x before 2.0.5 omits an overflow check in the tvb_get_guintvar function, which allows remote attackers to cause a denial of service (infinite loop) via a crafted packet, related to the MMSE, WAP, WBXML, and WSP dissectors.

## References
- http://www.securityfocus.com/bid/92174
- http://www.securitytracker.com/id/1036480
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=2193bea3212d74e2a907152055e27d409b59485e
- https://www.exploit-db.com/exploits/40195/
- http://www.wireshark.org/security/wnpa-sec-2016-48.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12661
- http://openwall.com/lists/oss-security/2016/07/28/3
