# [M] Silicon Labs EFR32 Bluetooth stack denial of service when sending notifications to multiple clients

## Summary
Severity: Medium
Advisory: CVE-2024-0240
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-15
Source: https://osv.dev/vulnerability/CVE-2024-0240
Type: osv

## Details
A memory leak in the Silicon Labs' Bluetooth stack for EFR32 products may cause memory to be exhausted when sending notifications to multiple clients, this results in all Bluetooth operations, such as advertising and scanning, to stop.

## References
- https://community.silabs.com/069Vm000001AjEfIAK
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0240.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0240
- https://github.com/SiliconLabs/gecko_sdk
- https://github.com/SiliconLabs/gecko_sdk/releases
