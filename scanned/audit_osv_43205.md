# [C] Grav CMS before 2.0.13 Remote Code Execution via Twig

## Summary
Severity: Critical
Advisory: CVE-2026-72827
Aliases: GHSA-xx48-97m4-h7qm
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/CVE-2026-72827
Type: osv

## Details
Grav CMS before 2.0.13 contains a server-side template injection vulnerability in email-action parameters that allows low-privileged page editors to execute arbitrary operating-system commands. Attackers can inject Twig payloads using the unsandboxed find filter in email subject, body, to, or from fields to achieve remote code execution when forms are submitted.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72827.json
- https://github.com/getgrav/grav/security/advisories/GHSA-xx48-97m4-h7qm
- https://nvd.nist.gov/vuln/detail/CVE-2026-72827
- https://www.vulncheck.com/advisories/grav-cms-before-remote-code-execution-via-twig
