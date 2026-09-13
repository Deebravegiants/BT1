# [H] GeometryCollection with strict-winding polygon causes server crash during 2dsphere index key generation

## Summary
Severity: High
Advisory: BIT-mongodb-2026-9752
Aliases: CVE-2026-9752
Ecosystem: Bitnami
Published: 2026-06-22
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-9752
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.3

## Details
An authorized user could trigger a server crash by running a query with a 2dsphere index on a field that stores a GeoJSON GeometryCollection containing a Polygon with a strict-winding CRS.

Strict-winding polygons are intentionally unsupported for indexing, but the guard that rejects them does not inspect members of a GeometryCollection, allowing the unsafe path to be reached which ends with an ensuing null-pointer dereference.

## References
- https://jira.mongodb.org/browse/SERVER-123440
- https://nvd.nist.gov/vuln/detail/CVE-2026-9752
