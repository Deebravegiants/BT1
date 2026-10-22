# [M] ZKsync Era evaluation order of Yul function arguments

## Summary
Severity: Medium
Advisory: CVE-2024-35229
Aliases: GHSA-jf9w-7f5g-j95p
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-05-27
Source: https://osv.dev/vulnerability/CVE-2024-35229
Type: osv

## Details
ZKsync Era is a layer 2 rollup that uses zero-knowledge proofs to scale Ethereum. Prior to version 1.3.10, there is a very specific pattern `f(a(),b()); check_if_a_executed_last()` in Yul that exposes a bug in evaluation order of Yul function arguments. This vulnerability has been fixed in version 1.3.10. As a workaround, update and redeploy affected contracts.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35229.json
- https://github.com/matter-labs/era-compiler-solidity/security/advisories/GHSA-jf9w-7f5g-j95p
- https://nvd.nist.gov/vuln/detail/CVE-2024-35229
- https://github.com/matter-labs/era-compiler-solidity/commit/46ce047b51576495779b9f67534207d8154eab79
