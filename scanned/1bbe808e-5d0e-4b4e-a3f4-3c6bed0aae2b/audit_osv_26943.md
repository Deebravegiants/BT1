# [H] Incorrect buffer parsing in Bluetooth LE sample code may lead to buffer overflow

## Summary
Severity: High
Advisory: CVE-2023-6387
CVSS: 7.5 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-02
Source: https://osv.dev/vulnerability/CVE-2023-6387
Type: osv

## Details
A potential buffer overflow exists in the Bluetooth LE HCI CPC sample application in the Gecko SDK which may result in a denial of service or remote code execution

## References
- https://community.silabs.com/069Vm000000WNKuIAO
- https://github.com/SiliconLabs/gecko_sdk/releases/tag/v4.4.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6387.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6387
