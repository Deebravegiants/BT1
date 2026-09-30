# [H] Out-of-Bounds Heap Read in BSON CodeWScope Element Parsing via Malformed BSONColumn Data

## Summary
Severity: High
Advisory: BIT-mongodb-2026-13077
Aliases: CVE-2026-13077
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-13077
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.7

## Details
A missing bounds check in the BSON CodeWScope element accessors allows an attacker to trigger an out-of-bounds heap read via a crafted aggregation pipeline. The vulnerability can be exploited by an authenticated user by generating a malformed BSONColumn data containing a CodeWScope element, bypassing wire-level BSON validation. When the forged element is decompressed, the unchecked size value is used in pointer arithmetic, causing either a server crash or disclosure of adjacent heap memory contents.

## References
- https://jira.mongodb.org/browse/SERVER-129103
- https://nvd.nist.gov/vuln/detail/CVE-2026-13077
