# [C] Command injection vulnerability in module management function in CloudExplorer Lite

## Summary
Severity: Critical
Advisory: CVE-2023-38692
Aliases: GHSA-7wrc-f42m-9v5w
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-08-04
Source: https://osv.dev/vulnerability/CVE-2023-38692
Type: osv

## Details
CloudExplorer Lite is an open source, lightweight cloud management platform. Versions prior to 1.3.1 contain a command injection vulnerability in the installation function in module management. The vulnerability has been fixed in v1.3.1. There are no known workarounds aside from upgrading.

## References
- https://github.com/CloudExplorer-Dev/CloudExplorer-Lite/blob/v1.3.0/framework/management-center/backend/src/main/java/com/fit2cloud/controller/ModuleManageController.java
- https://github.com/CloudExplorer-Dev/CloudExplorer-Lite/releases/tag/v1.3.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/38xxx/CVE-2023-38692.json
- https://github.com/CloudExplorer-Dev/CloudExplorer-Lite/security/advisories/GHSA-7wrc-f42m-9v5w
- https://nvd.nist.gov/vuln/detail/CVE-2023-38692
