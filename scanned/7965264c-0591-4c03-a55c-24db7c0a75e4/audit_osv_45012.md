# [C] ScadaBR Authenticated Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-9645
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-9645
Type: osv

## Details
Exposed methods allow authenticated users to create and execute arbitrary JavaScript code on the server. The scripts execute with full access, enabling complete system compromise as commands are executed as root.

## References
- https://www.tenable.com/security/research/tra-2026-46
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9645.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-9645
