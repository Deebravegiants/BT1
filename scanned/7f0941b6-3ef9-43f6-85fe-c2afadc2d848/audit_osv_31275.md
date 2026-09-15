# [M] Denial of Service in Silicon Labs RS9116 Bluetooth SDK

## Summary
Severity: Medium
Advisory: CVE-2024-7137
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-19
Source: https://osv.dev/vulnerability/CVE-2024-7137
Type: osv

## Details
The L2CAP receive data buffer for L2CAP packets is restricted to packet sizes smaller than the maximum supported packet size. Receiving a packet that exceeds the restricted buffer length may cause a crash. A hard reset is required to recover the crashed device.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/7xxx/CVE-2024-7137.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-7137
- https://community.silabs.com/068Vm00000I5mjD
- https://github.com/SiliconLabs/wiseconnect-wifi-bt-sdk
