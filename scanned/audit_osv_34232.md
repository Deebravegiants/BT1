# [H] CVE-2025-56365

## Summary
Severity: High
Advisory: CVE-2025-56365
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2025-56365
Type: osv

## Details
A reachable assertion vulnerability exists in the Matter SDK (connectedhomeip) before 1.4.0, in the interaction model command processing logic. When an InvokeCommandRequest is sent to a nonexistent endpoint and cluster (e.g., 0x34), the code incorrectly treats the endpoint as valid due to missing checks in CodegenDataModelProvider::Invoke. This causes a VerifyOrDie failure in ProcessCommandDataIB and results in a crash (SIGABRT). The issue has been acknowledged and fixed in a later revision (PR #37207).

## References
- https://github.com/project-chip/connectedhomeip/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/56xxx/CVE-2025-56365.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-56365
- https://github.com/project-chip/connectedhomeip/issues/37184
- https://github.com/project-chip/connectedhomeip/pull/37207
