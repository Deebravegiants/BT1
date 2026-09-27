# [M] osTicket (1.18.x < 1.18.3, 1.17.x < 1.17.7) PDF Export Arbitrary File Read

## Summary
Severity: Medium
Advisory: CVE-2026-22200
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-01-12
Source: https://osv.dev/vulnerability/CVE-2026-22200
Type: osv

## Details
Enhancesoft osTicket versions 1.18.x prior to 1.18.3 and 1.17.x prior to 1.17.7 contain an arbitrary file read vulnerability in the ticket PDF export functionality. A remote attacker can submit a ticket containing crafted rich-text HTML that includes PHP filter expressions which are insufficiently sanitized before being processed by the mPDF PDF generator during export. When the attacker exports the ticket to PDF, the generated PDF can embed the contents of attacker-selected files from the server filesystem as bitmap images, allowing disclosure of sensitive local files in the context of the osTicket application user. This issue is exploitable in default configurations where guests may create tickets and access ticket status, or where self-registration is enabled.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22200.json
- https://github.com/osTicket/osTicket/releases/tag/v1.17.7
- https://github.com/osTicket/osTicket/releases/tag/v1.18.3
- https://nvd.nist.gov/vuln/detail/CVE-2026-22200
- https://www.vulncheck.com/advisories/osticket-pdf-export-arbitrary-file-read
- https://github.com/osTicket/osTicket/commit/c59b067
- https://github.com/osTicket/osTicket
- https://horizon3.ai/attack-research/attack-blogs/ticket-to-shell-exploiting-php-filters-and-cnext-in-osticket-cve-2026-22200/
