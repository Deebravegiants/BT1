# [H] BlueZ Phone Book Access Profile Heap-based Buffer Overflow Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2023-50229
CVSS: 7.1 (CVSS:3.0/AV:A/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2023-50229
Type: osv

## Details
BlueZ Phone Book Access Profile Heap-based Buffer Overflow Remote Code Execution Vulnerability. This vulnerability allows network-adjacent attackers to execute arbitrary code on affected installations of BlueZ. User interaction is required to exploit this vulnerability in that the target must connect to a malicious Bluetooth device.

The specific flaw exists within the handling of the Phone Book Access profile. The issue results from the lack of proper validation of the length of user-supplied data prior to copying it to a fixed-length heap-based buffer. An attacker can leverage this vulnerability to execute code in the context of root. Was ZDI-CAN-20936.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00022.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/50xxx/CVE-2023-50229.json
- https://github.com/bluez/bluez/commit/5ab5352531a9cc7058cce569607f3a6831464443
- https://nvd.nist.gov/vuln/detail/CVE-2023-50229
- https://www.zerodayinitiative.com/advisories/ZDI-23-1811/
