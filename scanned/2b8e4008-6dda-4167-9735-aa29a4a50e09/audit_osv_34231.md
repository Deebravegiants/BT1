# [H] CVE-2025-56364

## Summary
Severity: High
Advisory: CVE-2025-56364
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2025-56364
Type: osv

## Details
A use of uninitialized value vulnerability exists in the Matter SDK (connectedhomeip) before 1.4.0, where the `GetDestinationGroupId().Value()` method is called without first checking whether a value exists. This leads to a crash when an InvokeCommand is sent without initializing the destination group ID. The issue affects all versions before commit 0360cc3 (Dec 5, 2024) and leads to denial of service through SIGABRT. It is fixed by adding a .HasValue() check before access.

## References
- https://github.com/project-chip/connectedhomeip/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/56xxx/CVE-2025-56364.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-56364
- https://github.com/project-chip/connectedhomeip/issues/36711
- https://github.com/project-chip/connectedhomeip/pull/36729
