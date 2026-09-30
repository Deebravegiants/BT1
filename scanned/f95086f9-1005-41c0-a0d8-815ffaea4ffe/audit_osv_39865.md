# [C] Compromised Nx Console version 18.95.0

## Summary
Severity: Critical
Advisory: CVE-2026-48027
Aliases: GHSA-c9j4-9m59-847w
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-48027
Type: osv

## Details
Nx Console is the user interface for Nx & Lerna. On 19 May 2026, a malicious version of Nx Console, 18.95.0, was published at 12:30 PM UTC and removed soon after at 12:48 PM UTC, leaving it available for ~18 minutes in Visual Studio Marketplace. For OpenVSX, the problem was detected later, and the compromised version was available from 12:33 UTC to 13:09 UTC (~36 minutes). Version 18.100.0 of Nx Console is not compromised and users may remediate by upgrading to that version.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2026-48027
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48027.json
- https://github.com/nrwl/nx-console/security/advisories/GHSA-c9j4-9m59-847w
- https://nvd.nist.gov/vuln/detail/CVE-2026-48027
- https://github.com/nrwl/nx-console/issues/3139
- https://nx.dev/blog/nx-console-v18-95-0-postmortem#indicators-of-compromise
- https://www.stepsecurity.io/blog/nx-console-vs-code-extension-compromised
