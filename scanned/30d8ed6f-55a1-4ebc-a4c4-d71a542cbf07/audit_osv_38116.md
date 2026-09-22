# [C] Zammad has a server-side template injection leading to RCE via AI Agent

## Summary
Severity: Critical
Advisory: CVE-2026-34724
Aliases: GHSA-fg9w-jg8f-4j94
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:H/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-34724
Type: osv

## Details
Zammad is a web based open source helpdesk/customer support system. Prior to 7.0.1, a server-side template injection vulnerability  which leads to RCE via AI Agent exists. Impact is limited to environments where an attacker can control or influence type_enrichment_data (typically high-privilege administrative configuration). This vulnerability is fixed in 7.0.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34724.json
- https://github.com/zammad/zammad/security/advisories/GHSA-fg9w-jg8f-4j94
- https://nvd.nist.gov/vuln/detail/CVE-2026-34724
