# [M] CVE-2020-26139

## Summary
Severity: Medium
Advisory: CVE-2020-26139
CVSS: 5.3 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-11
Source: https://osv.dev/vulnerability/CVE-2020-26139
Type: osv

## Details
An issue was discovered in the kernel in NetBSD 7.1. An Access Point (AP) forwards EAPOL frames to other clients even though the sender has not yet successfully authenticated to the AP. This might be abused in projected Wi-Fi networks to launch denial-of-service attacks against connected clients and makes it easier to exploit other vulnerabilities in connected clients.

## References
- http://www.openwall.com/lists/oss-security/2021/05/11/12
- https://github.com/vanhoefm/fragattacks/blob/master/SUMMARY.md
- https://lists.debian.org/debian-lts-announce/2021/06/msg00019.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00020.html
- https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-wifi-faf-22epcEWu
- https://www.arista.com/en/support/advisories-notices/security-advisories/12602-security-advisory-63
- https://www.fragattacks.com
- https://cert-portal.siemens.com/productcert/pdf/ssa-913875.pdf
