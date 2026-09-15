# [M] ZKsync Era invalid stack addressing conversion

## Summary
Severity: Medium
Advisory: CVE-2024-38533
Aliases: GHSA-q7pg-6jh9-87gv
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-06-28
Source: https://osv.dev/vulnerability/CVE-2024-38533
Type: osv

## Details
ZKsync Era is a layer 2 rollup that uses zero-knowledge proofs to scale Ethereum. There is possible invalid stack access due to the addresses used to access the stack not properly being converted to cells. This issue has been patched in version 1.5.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38533.json
- https://github.com/matter-labs/era-compiler-vyper/security/advisories/GHSA-q7pg-6jh9-87gv
- https://nvd.nist.gov/vuln/detail/CVE-2024-38533
