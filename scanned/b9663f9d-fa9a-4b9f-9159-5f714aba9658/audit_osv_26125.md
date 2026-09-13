# [M] BlueZ Audio Profile AVRCP avrcp_parse_attribute_list Out-Of-Bounds Read Information Disclosure Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2023-51580
CVSS: 5.4 (CVSS:3.0/AV:A/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:L)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2023-51580
Type: osv

## Details
BlueZ Audio Profile AVRCP avrcp_parse_attribute_list Out-Of-Bounds Read Information Disclosure Vulnerability. This vulnerability allows network-adjacent attackers to disclose sensitive information via Bluetooth on affected installations of BlueZ. User interaction is required to exploit this vulnerability in that the target must connect to a malicious device.

The specific flaw exists within the handling of the AVRCP protocol. The issue results from the lack of proper validation of user-supplied data, which can result in a read past the end of an allocated buffer. An attacker can leverage this in conjunction with other vulnerabilities to execute arbitrary code in the context of root. Was ZDI-CAN-20852.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/51xxx/CVE-2023-51580.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-51580
- https://www.zerodayinitiative.com/advisories/ZDI-23-1903/
