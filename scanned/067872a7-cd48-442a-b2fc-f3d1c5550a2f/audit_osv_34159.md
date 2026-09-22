# [C] aiven-db-migrate allows Privilege Escalation via unrestricted search_path during migration

## Summary
Severity: Critical
Advisory: CVE-2025-55282
Aliases: GHSA-hmvf-93r4-36f9
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-08-18
Source: https://osv.dev/vulnerability/CVE-2025-55282
Type: osv

## Details
aiven-db-migrate is an Aiven database migration tool. Prior to 1.0.7, there is a privilege escalation vulnerability that allows a user to elevate to superuser inside PostgreSQL databases during a migration from an untrusted source server. By exploiting a lack of search_path restriction, an attacker can override pg_catalog and execute untrusted operators as a superuser. This vulnerability is fixed in 1.0.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55282.json
- https://github.com/aiven/aiven-db-migrate/security/advisories/GHSA-hmvf-93r4-36f9
- https://nvd.nist.gov/vuln/detail/CVE-2025-55282
- https://github.com/aiven/aiven-db-migrate/commit/39517dc55720055d93262033b142a365f5bf92c5
