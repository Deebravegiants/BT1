# [H] CVE-2025-56361

## Summary
Severity: High
Advisory: CVE-2025-56361
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2025-56361
Type: osv

## Details
A reachable assertion vulnerability exists in the Matter SDK (connectedhomeip) 1.3 thru 1.4, specifically within the Level Control cluster's server tick logic (`emberAfLevelControlClusterServerTickCallback`). When a MoveToLevel command is executed and followed by a conflicting write to the OperationMode attribute (in the Pump Configuration and Control cluster), an invariant check (`minLevel < currentLevel`) fails and causes the device to abort. This leads to a denial of service condition. The issue is confirmed in SDK versions 1.3 and 1.4 (commit ab3d5ae), and is triggered remotely without authentication.

## References
- https://github.com/project-chip/connectedhomeip/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/56xxx/CVE-2025-56361.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-56361
- https://github.com/project-chip/connectedhomeip/issues/38619
