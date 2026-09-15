# [M] CVE-2020-26141

## Summary
Severity: Medium
Advisory: CVE-2020-26141
Aliases: 2869483, A-177911676, ASB-A-177911676
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-05-11
Source: https://osv.dev/vulnerability/CVE-2020-26141
Type: osv

## Details
An issue was discovered in the ALFA Windows 10 driver 6.1316.1209 for AWUS036H. The Wi-Fi implementation does not verify the Message Integrity Check (authenticity) of fragmented TKIP frames. An adversary can abuse this to inject and possibly decrypt packets in WPA or WPA2 networks that support the TKIP data-confidentiality protocol.

## References
- http://www.openwall.com/lists/oss-security/2021/05/11/12
- https://cert-portal.siemens.com/productcert/pdf/ssa-913875.pdf
- https://github.com/vanhoefm/fragattacks/blob/master/SUMMARY.md
- https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-wifi-faf-22epcEWu
- https://www.arista.com/en/support/advisories-notices/security-advisories/12602-security-advisory-63
- https://www.fragattacks.com
