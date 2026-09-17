# [H] OpenOLAT: Server-Side Template Injection (SSTI) in Velocity templates allows Remote Code Execution

## Summary
Severity: High
Advisory: CVE-2026-28228
Aliases: GHSA-55qg-vvgj-ffh4
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/CVE-2026-28228
Type: osv

## Details
OpenOlat is an open source web-based e-learning platform for teaching, learning, assessment and communication. Prior to versions 19.1.31, 20.1.18, and 20.2.5, an authenticated user with the Author role can inject Velocity directives into a reminder email template. When the reminder is processed (either triggered manually or via the daily cron job), the injected directives are evaluated server-side. By chaining Velocity's #set directive with Java reflection, an attacker can instantiate arbitrary Java classes such as java.lang.ProcessBuilder and execute operating system commands with the privileges of the Tomcat process (typically root in containerized deployments). This issue has been patched in versions 19.1.31, 20.1.18, and 20.2.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28228.json
- https://github.com/OpenOLAT/OpenOLAT/security/advisories/GHSA-55qg-vvgj-ffh4
- https://nvd.nist.gov/vuln/detail/CVE-2026-28228
