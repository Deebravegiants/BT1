# [M] CVE-2020-26147

## Summary
Severity: Medium
Advisory: CVE-2020-26147
CVSS: 5.4 (CVSS:3.1/AV:A/AC:H/PR:N/UI:R/S:U/C:L/I:H/A:N)
Published: 2021-05-11
Source: https://osv.dev/vulnerability/CVE-2020-26147
Type: osv

## Details
An issue was discovered in the Linux kernel 5.8.9. The WEP, WPA, WPA2, and WPA3 implementations reassemble fragments even though some of them were sent in plaintext. This vulnerability can be abused to inject packets and/or exfiltrate selected fragments when another device sends fragmented frames and the WEP, CCMP, or GCMP data-confidentiality protocol is used.

## References
- https://www.fragattacks.com
- https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-wifi-faf-22epcEWu
- https://www.arista.com/en/support/advisories-notices/security-advisories/12602-security-advisory-63
- https://cert-portal.siemens.com/productcert/pdf/ssa-913875.pdf
- https://github.com/vanhoefm/fragattacks/blob/master/SUMMARY.md
- https://lists.debian.org/debian-lts-announce/2021/06/msg00019.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00020.html
- http://www.openwall.com/lists/oss-security/2021/05/11/12
