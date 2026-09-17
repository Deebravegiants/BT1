# [H] macOS Archify: Local Privilege Escalation

## Summary
Severity: High
Advisory: CVE-2024-9062
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-10
Source: https://osv.dev/vulnerability/CVE-2024-9062
Type: osv

## Details
The Archify application contains a local privilege escalation vulnerability due to insufficient client validation in its privileged helper tool, com.oct4pie.archifyhelper, which is exposed via XPC. Archify follows the "factored applications" model, delegating privileged operations—such as arbitrary file deletion and file permission changes—to this helper running as root. However, the helper does not verify the code signature, entitlements, or signing flags of the connecting client. Although macOS provides secure validation mechanisms like auditToken, these are not implemented. As a result, any local process can establish a connection to the helper and invoke privileged functionality, leading to unauthorized execution of actions with root-level privileges.

## References
- https://pentraze.com/
- https://pentraze.com/vulnerability-reports/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/9xxx/CVE-2024-9062.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-9062
- https://github.com/Oct4Pie/archify
