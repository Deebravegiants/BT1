# [H] phpIPAM < 1.8.2 Authentication Bypass via REST API Object Cache

## Summary
Severity: High
Advisory: CVE-2026-67602
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-67602
Type: osv

## Details
phpIPAM before 1.8.2 contains an authentication bypass vulnerability in the REST API that allows unauthenticated attackers to gain full API access by exploiting an insecure object cache keying mechanism. The cache is keyed by lookup value alone without including the searched column, enabling an entry written during an app_id lookup to satisfy a subsequent app_code lookup, allowing attackers to use the numeric database row identifier as an API token to read, write, and delete all IP address management records.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67602.json
- https://github.com/phpipam/phpipam/releases/tag/v1.8.2
- https://nvd.nist.gov/vuln/detail/CVE-2026-67602
- https://www.vulncheck.com/advisories/phpipam-authentication-bypass-via-rest-api-object-cache
- https://github.com/phpipam/phpipam/commit/d29728fecca327f1ea825798908d0cfa4c62408e
- https://github.com/phpipam/phpipam
