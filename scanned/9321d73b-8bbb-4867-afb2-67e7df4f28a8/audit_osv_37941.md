# [H] LinkAce's SSRF protection can be bypassed via internal hostname resolution in LinkAce

## Summary
Severity: High
Advisory: CVE-2026-33953
Aliases: GHSA-wp4g-qw9j-wfjg
CVSS: 8.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-33953
Type: osv

## Details
LinkAce is a self-hosted archive to collect website links. Versions prior to 2.5.3 block direct requests to private IP literals, but still performs server-side requests to internal-only resources when those resources are referenced through an internal hostname. This allows an authenticated user to trigger server-side requests to internal services reachable by the LinkAce server but not directly reachable by an external user. Version 2.5.3 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33953.json
- https://github.com/Kovah/LinkAce/security/advisories/GHSA-wp4g-qw9j-wfjg
- https://nvd.nist.gov/vuln/detail/CVE-2026-33953
