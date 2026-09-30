# [C] Cachet 2.4.1 Authenticated Server-Side Template Injection RCE

## Summary
Severity: Critical
Advisory: CVE-2026-69118
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-69118
Type: osv

## Details
Cachet through 2.4.1 contains a server-side template injection vulnerability in incident template rendering that allows authenticated users to execute arbitrary PHP code. Attackers can create malicious incident templates with Blade directives or Twig filters that execute system commands when incidents are created, achieving remote code execution as the web server process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69118.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-69118
- https://www.vulncheck.com/advisories/cachet-authenticated-server-side-template-injection-rce
- https://github.com/cachethq/cachet
- https://github.com/cachethq/cachet/issues/4621
