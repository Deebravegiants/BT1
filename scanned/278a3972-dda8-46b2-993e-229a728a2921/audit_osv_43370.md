# [H] PostGIS < 3.7.0beta2 Out-of-Bounds Read via FlatGeobuf Buffer

## Summary
Severity: High
Advisory: CVE-2026-73515
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73515
Type: osv

## Details
PostGIS before 3.7.0beta2 contains an out-of-bounds read vulnerability that allows attackers to cause memory disclosure or a server crash by supplying a malformed FlatGeobuf buffer. The FlatGeobuf property metadata decoder verifies that a string length field is present but fails to verify that the subsequent string body is contained within the supplied buffer before materializing it into a SQL-visible value, enabling memory disclosure or denial of service.

## References
- https://gitea.osgeo.org/postgis/postgis/raw/tag/3.7.0beta2/NEWS
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73515.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-73515
- https://www.vulncheck.com/advisories/postgis-0beta2-out-of-bounds-read-via-flatgeobuf-buffer
- https://github.com/postgis/postgis
- https://mehmetince.net/part-1-6-systemic-risks-in-the-managed-postgresql-industry-extension-risks-are-real-exploiting-postgis-memory-corruption-bug-at-neondb-supabase-and-many-more/
