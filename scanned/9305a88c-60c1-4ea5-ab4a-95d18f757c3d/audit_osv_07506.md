# [C] BIT-sqlite-2025-3277

## Summary
Severity: Critical
Advisory: BIT-sqlite-2025-3277
Aliases: CVE-2025-3277
Ecosystem: Bitnami
Published: 2025-04-16
Source: https://osv.dev/vulnerability/BIT-sqlite-2025-3277
Type: osv

## Affected
- Bitnami: `sqlite` — affected >=3.44.0 <3.49.1

## Details
An integer overflow can be triggered in SQLite’s `concat_ws()` function. The resulting, truncated integer is then used to allocate a buffer. When SQLite then writes the resulting string to the buffer, it uses the original, untruncated size and thus a wild Heap Buffer overflow of size ~4GB can be triggered. This can result in arbitrary code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3277
- https://sqlite.org/src/info/498e3f1cf57f164f
