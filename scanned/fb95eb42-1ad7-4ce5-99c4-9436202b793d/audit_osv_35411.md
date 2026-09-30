# [C] Cal.com before 5.9.9 Remote Code Execution via RSC

## Summary
Severity: Critical
Advisory: CVE-2025-71389
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2025-71389
Type: osv

## Details
Cal.com (calcom/cal.diy) before 5.9.9 is vulnerable to unauthenticated remote code execution because it bundles a version of Next.js whose React Server Components (RSC) request handling deserializes attacker-controlled input. A remote attacker can send a crafted RSC request to the server and cause arbitrary code to be executed during server-side processing, without authentication or user interaction. The flaw derives from the upstream Next.js vulnerability CVE-2025-55182 and is resolved in 5.9.9 by updating the affected dependency.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71389.json
- https://github.com/advisories/GHSA-9qr9-h5gf-34mp
- https://github.com/calcom/cal.diy/security/advisories/GHSA-qjx2-5xqp-cpf4
- https://nvd.nist.gov/vuln/detail/CVE-2025-71389
- https://www.vulncheck.com/advisories/cal-com-before-remote-code-execution-via-rsc
- https://github.com/calcom/cal.diy/pull/25592
