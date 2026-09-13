# [H] CVE-2025-56362

## Summary
Severity: High
Advisory: CVE-2025-56362
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2025-56362
Type: osv

## Details
A reachable assertion vulnerability exists in the Matter SDK (connectedhomeip) before 1.4.2, specifically within the Level Control cluster's periodic server tick logic. When a MoveToLevel command is sent and immediately followed by a write of OperationMode=2 (in the Pump Configuration and Control cluster), the server tick function violates the assertion `currentLevel < maxLevel`, resulting in a crash. This can be exploited remotely without authentication to cause denial of service. Affected versions include 1.3 and 1.4 (commit ab3d5ae).

## References
- https://github.com/project-chip/connectedhomeip/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/56xxx/CVE-2025-56362.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-56362
- https://github.com/project-chip/connectedhomeip/issues/38618
