# [M] Dokploy has a clickjacking vulnerability - Missing X-Frame-Options and CSP frame-ancestors headers

## Summary
Severity: Medium
Advisory: CVE-2026-24839
Aliases: GHSA-c94j-8wgf-2q9q
CVSS: 4.7 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:L/A:N)
Published: 2026-01-28
Source: https://osv.dev/vulnerability/CVE-2026-24839
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). In versions prior to 0.26.6, the Dokploy web interface is vulnerable to Clickjacking attacks due to missing frame-busting headers. This allows attackers to embed Dokploy pages in malicious iframes and trick authenticated users into performing unintended actions. Version 0.26.6 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24839.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-c94j-8wgf-2q9q
- https://nvd.nist.gov/vuln/detail/CVE-2026-24839
- https://github.com/Dokploy/dokploy/commit/9714695d5a78fe24496f989ab81807ba04699df8
- https://github.com/Dokploy/dokploy/pull/3500
