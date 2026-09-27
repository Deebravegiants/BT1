# [M] Zigbee Router Denial of Service

## Summary
Severity: Medium
Advisory: CVE-2025-7964
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H)
Published: 2026-01-30
Source: https://osv.dev/vulnerability/CVE-2025-7964
Type: osv

## Details
After receiving a 

malformed 802.15.4 MAC Data Request

 the Zigbee Coordinator sends a ‘network leave’ request to Zigbee router resulting in the Zigbee Router getting stuck in a non-rejoinable state. If a suitable parent is not available, the end devices will be unable to rejoin. A manual recommissioning is required to recover the Zigbee Router.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/7xxx/CVE-2025-7964.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-7964
- https://community.silabs.com/068Vm00000dspiL
- https://github.com/SiliconLabs/gecko_sdk
- https://github.com/SiliconLabs/simplicity_sdk
