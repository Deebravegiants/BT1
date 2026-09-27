# [C] Dokploy: Remote Code Execution via destinationPath in Container File Upload

## Summary
Severity: Critical
Advisory: CVE-2026-45663
Aliases: GHSA-9m66-74x3-5mwr
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-45663
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). In 0.29.1 and earlier, a command injection vulnerability exists in the Docker file upload functionality. When an authenticated user uploads a file to a container, the destinationPath parameter is not properly sanitized and is directly interpolated into a shell command string. By including shell metacharacters such as ; or ", an attacker can escape the intended docker cp command and execute arbitrary OS commands on the Dokploy host.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45663.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-9m66-74x3-5mwr
- https://nvd.nist.gov/vuln/detail/CVE-2026-45663
