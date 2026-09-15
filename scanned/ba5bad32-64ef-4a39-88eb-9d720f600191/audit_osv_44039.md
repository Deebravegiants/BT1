# [M] Ghostwriter before 7.1.2 Cross-Client Report Template Disclosure via Unauthorized Template Swap

## Summary
Severity: Medium
Advisory: CVE-2026-78203
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-78203
Type: osv

## Details
Ghostwriter before 7.1.2 fails to validate template ownership in the report template swap endpoint, allowing attackers to attach client-scoped templates from other clients to their own reports. Attackers can exploit sequential template primary keys to enumerate and attach foreign templates, then generate reports to disclose template contents including letterhead, boilerplate, and methodology text.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78203.json
- https://github.com/geo-chen/oss/blob/main/Ghostwriter.md
- https://nvd.nist.gov/vuln/detail/CVE-2026-78203
- https://www.vulncheck.com/advisories/ghostwriter-before-cross-client-report-template-disclosure-via-unauthorized-template-swap
- https://github.com/GhostManager/Ghostwriter/commit/5b2a4a297e44c823c16f65b1ba101c742791cd0b
- https://github.com/GhostManager/Ghostwriter
- https://github.com/GhostManager/Ghostwriter/blob/v7.1.1/ghostwriter/reporting/views.py#L275-L315
