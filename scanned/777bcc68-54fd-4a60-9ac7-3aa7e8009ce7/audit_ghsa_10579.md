# [C] go-zserio has Unbounded Memory Allocation for All Platforms

## Summary
Severity: Critical
Advisory: GHSA-xhj4-g6w8-2xjw
CWE: CWE-789
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-xhj4-g6w8-2xjw
Type: github-advisory

## Affected
- Go: `github.com/woven-planet/go-zserio` — affected >=0 <0.9.1

## Details
### Impact

When deserializing arrays, strings or bytes (blob) types zserio first reads the size of the variable, and then allocates sufficient memory to load data. Since the size is always trusted this can be abused by creating a data file with a large size value, causing the zserio runtime to allocate large amounts of memory.

### Patches

Please apply [this commit](https://github.com/woven-by-toyota/go-zserio/commit/39ef1decde7e9766207794d396018776b33c6e45).

### Workarounds

- Do not accept zserio data from non-trusted sources.
- Use secure transportation protocols (like TLS).

## References
- https://github.com/woven-by-toyota/go-zserio/security/advisories/GHSA-xhj4-g6w8-2xjw
- https://github.com/woven-by-toyota/go-zserio/commit/39ef1decde7e9766207794d396018776b33c6e45
- https://github.com/woven-by-toyota/go-zserio
