# [H] Yapscan Denial of Service vulnerability in report server

## Summary
Severity: High
Advisory: GHSA-wxwq-525w-hcqx
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-03
Source: https://github.com/advisories/GHSA-wxwq-525w-hcqx
Type: github-advisory

## Affected
- Go: `github.com/fkie-cad/yapscan` — affected >=0.18.0 <0.19.2

## Details
### Impact

If you use the report server, it may be vulnerable to a Denial of Service attack.

### Patches

Has been patched in v0.19.2.

### References

The vulnerability was inherited by the following upstream vulnerabilites

- [golang.org/x/text < v0.3.7](https://github.com/advisories/GHSA-ppp9-7jff-5vj2)
- [golang.org/x/net < 0.0.0-20220906165146-f3363e06e74c](https://github.com/advisories/GHSA-69cg-p879-7622)

## References
- https://github.com/fkie-cad/yapscan/security/advisories/GHSA-wxwq-525w-hcqx
- https://github.com/fkie-cad/yapscan/pull/46
- https://github.com/fkie-cad/yapscan/commit/242b4b25b107deacddd4ca276b45d23e16bb3b88
- https://github.com/fkie-cad/yapscan/commit/65f277662c6475eb3f592e0e4fdfee902ecd9326
- https://github.com/advisories/GHSA-69cg-p879-7622
- https://github.com/advisories/GHSA-ppp9-7jff-5vj2
- https://github.com/fkie-cad/yapscan
- https://github.com/fkie-cad/yapscan/releases/tag/v0.19.2
