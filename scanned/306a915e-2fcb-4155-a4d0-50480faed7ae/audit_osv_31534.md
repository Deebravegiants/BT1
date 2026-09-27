# [M] Denial of Service (DoS) vulnerabilitiey in Zigbee library

## Summary
Severity: Medium
Advisory: CVE-2025-1394
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2025-07-30
Source: https://osv.dev/vulnerability/CVE-2025-1394
Type: osv

## Details
The Ember ZNet stack’s packet buffer manager may read out of bound memory leading to an assert, causing a Denial of Service (DoS).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/1xxx/CVE-2025-1394.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-1394
- https://www.silabs.com/documents/public/release-notes/emberznet-release-notes-7.5.0.0.pdf
- https://www.silabs.com/documents/public/release-notes/emberznet-release-notes-8.0.3.0.pdf
- https://www.silabs.com/documents/public/release-notes/emberznet-release-notes-8.1.0.0.pdf
- https://community.silabs.com/068Vm00000SkHNX
- https://github.com/SiliconLabs/gecko_sdk
- https://github.com/SiliconLabs/simplicity_sdk
