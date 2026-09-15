# [H] Dgraph: DQL Injection via unvalidated regexp filter argument in GraphQL query rewriter

## Summary
Severity: High
Advisory: CVE-2026-63637
Aliases: GHSA-33p8-wc97-5qcj
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-63637
Type: osv

## Details
Dgraph is an open source distributed GraphQL database. Prior to 25.3.8, maybeQuoteArg in graphql/resolve/query_rewriter.go passes regexp filter strings into generated DQL without quoting or validating the /pattern/flags form, allowing crafted GraphQL query or mutation filters to inject DQL operators, disclose unintended nodes, or expand modification and deletion targets. This issue is fixed in version 25.3.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63637.json
- https://github.com/dgraph-io/dgraph/security/advisories/GHSA-33p8-wc97-5qcj
- https://nvd.nist.gov/vuln/detail/CVE-2026-63637
- https://github.com/dgraph-io/dgraph/commit/aaff09ab9608f87d88e9d601e71d271306083392
