# [M] PostgreSQL Anonymizer: Unrestricted function can leak the secret salt

## Summary
Severity: Medium
Advisory: CVE-2026-13455
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-13455
Type: osv

## Details
PostgreSQL Anonymizer contains a vulnerability that allows unprivileged masked users to repeatedly call the anon.hash() function and collects (seed, hash_output) pairs to perform an offline brute-force attack and deduce the salt. The problem is resolved in PostgreSQL Anonymizer 3.1.2 and later versions

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13455.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-13455
- https://gitlab.com/dalibo/postgresql_anonymizer/-/issues/649
