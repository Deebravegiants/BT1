# [C] ScadaLTS Authenticated Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-19656
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-19656
Type: osv

## Details
ScadaLTS 2.7.8.1 exposes a server-side method that lacks authorization checks, allowing any authenticated user (including one holding only low-privilege, read-only permissions) to execute arbitrary operating system commands on the host. Successful exploitation results in code execution in the context of the ScadaLTS server process (root), leading to full compromise of the underlying system.

## References
- https://www.tenable.com/security/research/tra-2026-55
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19656.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-19656
