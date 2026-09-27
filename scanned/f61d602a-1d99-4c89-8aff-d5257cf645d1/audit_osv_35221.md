# [C] Titra has Remote Code Execution in Admin Functionality

## Summary
Severity: Critical
Advisory: CVE-2025-69288
Aliases: GHSA-pqgx-6wg3-gmvr
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-12-31
Source: https://osv.dev/vulnerability/CVE-2025-69288
Type: osv

## Details
Titra is open source project time tracking software. Prior to version 0.99.49, Titra allows any authenticated Admin user to modify the timeEntryRule in the database. The value is then passed to a NodeVM value to execute as code. Without sanitization, it leads to a Remote Code Execution. Version 0.99.49 fixes the issue.

## References
- https://github.com/kromitgmbh/titra/releases/tag/0.99.49
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69288.json
- https://github.com/kromitgmbh/titra/security/advisories/GHSA-pqgx-6wg3-gmvr
- https://nvd.nist.gov/vuln/detail/CVE-2025-69288
- https://github.com/kromitgmbh/titra/commit/2e2ac5cbeed47a76720b21c7fde0214a242e065e
