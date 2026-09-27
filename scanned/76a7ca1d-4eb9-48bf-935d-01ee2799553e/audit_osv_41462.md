# [H] Apache CloudStack: Get and Run Diagnostics Command Injection

## Summary
Severity: High
Advisory: CVE-2026-61400
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-61400
Type: osv

## Details
Improper Neutralization of Special Elements used in a Command ('Command Injection') vulnerability in Apache CloudStack's run and get diagnostics functionality for the system VMs and virtual routers.

An authenticated user holding the permissions required to invoke either `getDiagnosticsData` or `runDiagnostics` can achieve arbitrary command execution on the system VM and/or Virtual Router instances, with commands running as root (or as the diagnostics-process user, at minimum). This represents a full compromise of the affected instance and, depending on network segmentation, may provide a foothold for lateral movement within the CloudStack-managed infrastructure, including access to guest network traffic handled by the compromised Virtual Router.



The getDiagnosticsData and runDiagnostics APIs are restricted to only Admin role accounts by default.


This issue affects Apache CloudStack: from 4.20.0.0 through 4.20.3.0 and from 4.21.0.0 through 4.22.1.0.

Users are recommended to upgrade to version 4.20.3.1 or 4.22.1.1 or later, which fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61400.json
- https://lists.apache.org/thread/g6cwddtjrwbh1d56wjz4cfp3fzfm4kbc
- https://nvd.nist.gov/vuln/detail/CVE-2026-61400
