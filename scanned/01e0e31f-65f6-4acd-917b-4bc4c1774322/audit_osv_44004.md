# [H] toml-node: Uncontrolled Recursion

## Summary
Severity: High
Advisory: CVE-2026-77465
Aliases: GHSA-82x6-q7mm-w9cf
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-77465
Type: osv

## Details
toml-node is a TOML parser for Node.js and the browser. Prior to 4.2.0, toml.parse() uses a Peggy 5.1.0 generated recursive-descent parser in lib/parser.js whose peg$parsevalue, peg$parsearray, and peg$parseinline_table_entry functions recurse through nested arrays and inline tables without a depth limit. A remote unauthenticated application parsing an attacker-controlled TOML document containing a few thousand nested arrays or inline tables can exhaust the Node.js call stack, raise an unexpected RangeError rather than the parser's SyntaxError, and terminate an unprotected request worker or process. The corresponding grammar source is src/toml.pegjs, where the generated parser must be bounded. This issue is fixed in version 4.2.0.

## References
- https://github.com/BinaryMuse/toml-node/security/advisories/GHSA-82x6-q7mm-w9cf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77465.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-77465
- https://github.com/BinaryMuse/toml-node/commit/967b8b06754f3ecd9863cea118dc50792a8c353f
- https://github.com/BinaryMuse/toml-node/pull/72
