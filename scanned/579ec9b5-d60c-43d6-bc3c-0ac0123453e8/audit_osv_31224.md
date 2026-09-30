# [M] EmberZNet malformed MAC layer packet leads to denial of service

## Summary
Severity: Medium
Advisory: CVE-2024-6350
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-08
Source: https://osv.dev/vulnerability/CVE-2024-6350
Type: osv

## Details
A malformed 802.15.4 packet causes a buffer overflow to occur leading to an assert and a denial of service. A watchdog reset clears the error condition automatically.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6350.json
- https://github.com/SiliconLabs/simplicity_sdk/releases
- https://nvd.nist.gov/vuln/detail/CVE-2024-6350
- https://community.silabs.com/069Vm00000HtvDgIAJ
- https://github.com/SiliconLabs/simplicity_sdk
