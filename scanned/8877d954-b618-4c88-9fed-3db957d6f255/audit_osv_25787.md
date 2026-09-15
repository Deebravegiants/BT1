# [H] BlueZ Audio Profile AVRCP Stack-based Buffer Overflow Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2023-44431
CVSS: 7.1 (CVSS:3.0/AV:A/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2023-44431
Type: osv

## Details
BlueZ Audio Profile AVRCP Stack-based Buffer Overflow Remote Code Execution Vulnerability. This vulnerability allows network-adjacent attackers to execute arbitrary code via Bluetooth on affected installations of BlueZ. User interaction is required to exploit this vulnerability in that the target must connect to a malicious device.

The specific flaw exists within the handling of the AVRCP protocol. The issue results from the lack of proper validation of the length of user-supplied data prior to copying it to a fixed-length stack-based buffer. An attacker can leverage this vulnerability to execute code in the context of root. Was ZDI-CAN-19909.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/44xxx/CVE-2023-44431.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-44431
- https://www.zerodayinitiative.com/advisories/ZDI-23-1900/
