# [C] Microsoft Container Migration Solution Accelerator: Authenticated IDOR allowing read/write/delete processes

## Summary
Severity: Critical
Advisory: CVE-2026-73298
Aliases: GHSA-27mc-pccp-3x2x
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-73298
Type: osv

## Details
The Microsoft Container Migration Solution Accelerator is a multi-service application that provides a multi-agent, AI-driven migration solution for moving container service configurations to Azure Kubernetes Service. In version 2.1.2 and earlier, a security vulnerability was identified in the Container Migration Solution Accelerator, specifically an authenticated IDOR (Insecure Direct Object Reference) that allows users to read, write, and delete processes belonging to other authenticated users. The issue affects multiple API endpoints, where ownership checks are missing, enabling unauthorized access and modification of migration data across users within the same organization. The vulnerability is present in both process and file management APIs, and the application relies on Entra ID authentication but lacks proper authorization controls between users. Authenticated users are able to access, modify, and delete processes and files belonging to other users without proper authorization checks.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73298.json
- https://github.com/microsoft/Container-Migration-Solution-Accelerator/security/advisories/GHSA-27mc-pccp-3x2x
- https://nvd.nist.gov/vuln/detail/CVE-2026-73298
