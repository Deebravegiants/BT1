# [H] bunkerweb: Improper Input Validation and Improper Neutralization of Special Elements in Output Used by a Downstream Component ('Injection') in BunkerWeb

## Summary
Severity: High
Advisory: CVE-2026-54728
Aliases: GHSA-254j-92cv-m443
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-54728
Type: osv

## Details
bunkerweb is an Open-source and next-generation Web Application Firewall (WAF). Prior to BunkerWeb 1.6.12 and BunkerWeb PRO 0.57, authenticated Host header handling in the BunkerWeb UI and API improperly validated and neutralized user-controlled input in a configuration-dependent path, allowing a low-privileged authenticated user to escalate privileges and affect confidentiality, integrity, and availability of the BunkerWeb instance. This issue is fixed in BunkerWeb version 1.6.12 and BunkerWeb PRO version 0.57.

## References
- https://github.com/bunkerity/bunkerweb/releases/tag/v1.6.12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54728.json
- https://github.com/bunkerity/bunkerweb/security/advisories/GHSA-254j-92cv-m443
- https://nvd.nist.gov/vuln/detail/CVE-2026-54728
- https://github.com/bunkerity/bunkerweb/commit/685ccbbe7d204132a843a7b7fd802d1bdb3f20a9
