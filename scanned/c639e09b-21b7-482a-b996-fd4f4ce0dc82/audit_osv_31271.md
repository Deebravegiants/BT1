# [C] Server-Side Template Injection in Dispatch Message Templates

## Summary
Severity: Critical
Advisory: CVE-2024-7093
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2024-08-01
Source: https://osv.dev/vulnerability/CVE-2024-7093
Type: osv

## Details
Dispatch's notification service uses Jinja templates to generate messages to users. Jinja permits code execution within blocks, which were neither properly sanitized nor sandboxed. This vulnerability enables users to construct command line scripts in their custom message templates, which are then executed whenever these notifications are rendered and sent out.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/7xxx/CVE-2024-7093.json
- https://github.com/Netflix/security-bulletins/blob/master/advisories/nflx-2024-003.md
- https://nvd.nist.gov/vuln/detail/CVE-2024-7093
- https://github.com/Netflix/dispatch
