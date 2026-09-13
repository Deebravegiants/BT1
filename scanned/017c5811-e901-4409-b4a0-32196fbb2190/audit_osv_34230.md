# [H] CVE-2025-56363

## Summary
Severity: High
Advisory: CVE-2025-56363
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2025-56363
Type: osv

## Details
A null pointer dereference vulnerability exists in the Matter SDK (connectedhomeip) before 1.4.0, affecting the ReadRevisionAttribute function used in multiple clusters (Channel, Account Login, TargetNavigator, etc.). The function lacks proper validation of the delegate pointer before dereferencing. A remote unauthenticated attacker can exploit this issue by sending a crafted read request, causing the device to crash (denial of service). This issue has been confirmed in SDK version v1.4 (commit ab3d5ae).

## References
- https://github.com/project-chip/connectedhomeip/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/56xxx/CVE-2025-56363.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-56363
- https://github.com/project-chip/connectedhomeip/issues/39173
