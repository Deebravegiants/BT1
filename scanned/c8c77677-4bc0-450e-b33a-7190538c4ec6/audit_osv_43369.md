# [C] PostGIS address_standardizer Out-of-Bounds Write via standardize_address()

## Summary
Severity: Critical
Advisory: CVE-2026-73514
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73514
Type: osv

## Details
The address_standardizer extension for PostGIS through 3.7.0, fixed in commit 423570b, contains an out-of-bounds write vulnerability that allows a database user with the ability to supply caller-controlled relation names to standardize_address() to trigger memory corruption by providing a rules table with a classification Type value exceeding the fixed class range. Attackers can craft a malicious rules table entry with an oversized rule type value that is used without bounds checking as an index into an internal output-link table, resulting in an out-of-bounds write.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73514.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-73514
- https://www.vulncheck.com/advisories/postgis-address-standardizer-out-of-bounds-write-via-standardize-address
- https://github.com/postgis/address_standardizer/pull/3
- https://github.com/postgis/address_standardizer/commit/423570b0dbf6cd9f6fc36de28a636e7b6e9aa8aa
- https://github.com/postgis/address_standardizer/pull/4
- https://github.com/postgis/address_standardizer
- https://mehmetince.net/part-1-6-systemic-risks-in-the-managed-postgresql-industry-extension-risks-are-real-exploiting-postgis-memory-corruption-bug-at-neondb-supabase-and-many-more/
