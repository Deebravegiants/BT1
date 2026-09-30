# [H] Incorrect results returned from Rows.Scan in database/sql

## Summary
Severity: High
Advisory: BIT-golang-2025-47907
Aliases: CVE-2025-47907, GO-2025-3849
Ecosystem: Bitnami
Published: 2025-08-10
Source: https://osv.dev/vulnerability/BIT-golang-2025-47907
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.24.0 <1.24.6

## Details
Cancelling a query (e.g. by cancelling the context passed to one of the query methods) during a call to the Scan method of the returned Rows can result in unexpected results if other queries are being made in parallel. This can result in a race condition that may overwrite the expected results with those of another query, causing the call to Scan to return either unexpected results from the other query or an error.

## References
- https://go.dev/cl/693735
- https://go.dev/issue/74831
- https://groups.google.com/g/golang-announce/c/x5MKroML2yM
- https://nvd.nist.gov/vuln/detail/CVE-2025-47907
- https://pkg.go.dev/vuln/GO-2025-3849
- http://www.openwall.com/lists/oss-security/2025/08/06/1
