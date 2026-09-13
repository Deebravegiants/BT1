# [H] LinkAce: Setup database password newline injection enables pre-auth RCE on uninitialized instances

## Summary
Severity: High
Advisory: CVE-2026-45344
Aliases: GHSA-37m5-936h-w455
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-45344
Type: osv

## Details
LinkAce is a self-hosted archive to collect website links. Prior to 2.5.6, the setup database configuration flow on uninitialized LinkAce instances accepts attacker-controlled database credential fields and writes them back into .env without escaping. A remote attacker who can reach the setup endpoints and supply a database they control can inject mail configuration variables and achieve command execution when the application later sends mail. This vulnerability is fixed in 2.5.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45344.json
- https://github.com/Kovah/LinkAce/security/advisories/GHSA-37m5-936h-w455
- https://nvd.nist.gov/vuln/detail/CVE-2026-45344
