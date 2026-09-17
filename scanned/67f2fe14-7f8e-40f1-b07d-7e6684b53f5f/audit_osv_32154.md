# [C] OpenCTI has remote code execution and sensitive secrets exposed through web hook

## Summary
Severity: Critical
Advisory: CVE-2025-24977
Aliases: GHSA-mf88-g2wq-p7qm, PYSEC-2025-179
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-05-05
Source: https://osv.dev/vulnerability/CVE-2025-24977
Type: osv

## Details
OpenCTI is an open cyber threat intelligence (CTI) platform. Prior to version 6.4.11 any user with the capability `manage customizations` can execute commands on the underlying infrastructure where OpenCTI is hosted and can access internal server side secrets by misusing the web-hooks. Since the malicious user gets a root shell inside a container this opens up the the infrastructure environment for further attacks and exposures. Version 6.4.11 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24977.json
- https://github.com/OpenCTI-Platform/opencti/security/advisories/GHSA-mf88-g2wq-p7qm
- https://nvd.nist.gov/vuln/detail/CVE-2025-24977
