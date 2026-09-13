# [H] BlueZ Audio Profile AVRCP Improper Validation of Array Index Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2023-27349
CVSS: 7.1 (CVSS:3.0/AV:A/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2023-27349
Type: osv

## Details
BlueZ Audio Profile AVRCP Improper Validation of Array Index Remote Code Execution Vulnerability. This vulnerability allows network-adjacent attackers to execute arbitrary code via Bluetooth on affected installations of BlueZ. User interaction is required to exploit this vulnerability in that the target must connect to a malicious device.

The specific flaw exists within the handling of the AVRCP protocol. The issue results from the lack of proper validation of user-supplied data, which can result in a write past the end of an allocated buffer. An attacker can leverage this vulnerability to execute code in the context of root. Was ZDI-CAN-19908.

## References
- https://lists.debian.org/debian-lts-announce/2024/05/msg00015.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00022.html
- https://git.kernel.org/pub/scm/bluetooth/bluez.git/commit/?id=f54299a850676d92c3dafd83e9174fcfe420ccc9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27349.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-27349
- https://www.zerodayinitiative.com/advisories/ZDI-23-386/
