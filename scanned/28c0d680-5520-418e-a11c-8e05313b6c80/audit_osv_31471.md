# [M] DoS in Zigbee device due to heavy traffic

## Summary
Severity: Medium
Advisory: CVE-2025-1221
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2025-07-30
Source: https://osv.dev/vulnerability/CVE-2025-1221
Type: osv

## Details
A Zigbee Radio Co-Processor (RCP), which is using SiLabs EmberZNet Zigbee stack, was unable to send messages to the host system (CPCd) due to heavy Zigbee traffic, resulting in a Denial of Service (DoS) attack, Only hard reset will bring the device to normal operation

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/1xxx/CVE-2025-1221.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-1221
- https://www.silabs.com/documents/public/release-notes/emberznet-release-notes-7.4.4.0.pdf
- https://www.silabs.com/documents/public/release-notes/emberznet-release-notes-8.0.2.0.pdf
- https://www.silabs.com/documents/public/release-notes/emberznet-release-notes-8.1.0.0.pdf
- https://community.silabs.com/068Vm00000Sadyn
- https://github.com/SiliconLabs/gecko_sdk
- https://github.com/SiliconLabs/simplicity_sdk
