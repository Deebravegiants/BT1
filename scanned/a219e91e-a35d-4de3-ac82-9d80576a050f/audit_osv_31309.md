# [H] DoS caused due to wrong hash length returned for SHA2/224 algorithm

## Summary
Severity: High
Advisory: CVE-2024-8361
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-07
Source: https://osv.dev/vulnerability/CVE-2024-8361
Type: osv

## Details
In SiWx91x devices, the SHA2/224 algorithm returns a hash of 256 bits instead of 224 bits. This incorrect hash length triggers a software assertion, which subsequently causes a Denial of Service (DoS).
If a watchdog is implemented, device will restart after watch dog expires. If watchdog is not implemented, device can be recovered only after a hard reset

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/8xxx/CVE-2024-8361.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-8361
- https://community.silabs.com/068Vm00000I7zqo
- https://github.com/SiliconLabs/wiseconnect
