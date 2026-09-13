# [M] OpenZeppelin Contracts and Contracts Upgradeable duplicated execution of subcalls in v4.9.4

## Summary
Severity: Medium
Advisory: GHSA-699g-q6qh-q4v8
CVE: CVE-2023-49798
CWE: CWE-670
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-12-12
Source: https://github.com/advisories/GHSA-699g-q6qh-q4v8
Type: github-advisory

## Affected
- npm: `@openzeppelin/contracts` — affected >=4.9.4 <4.9.5
- npm: `@openzeppelin/contracts-upgradeable` — affected >=4.9.4 <4.9.5

## Details
### Context
Merge conflict resolution issue when porting the v5.0.1 `Multicall` update to the v4.9 branch caused a duplicated line.

### Impact
Versions using `Multicall` from `@openzeppelin/contracts@4.9.4` and `@openzeppelin/contracts-upgradeable@4.9.4` will execute each subcall twice. Concretely, this exposes a user to unintentionally duplicate operations like asset transfers.

### Patches
The duplicated `delegatecall` was removed in 4.9.5. The 4.9.4 version is marked as deprecated.

## References
- https://github.com/OpenZeppelin/openzeppelin-contracts/security/advisories/GHSA-699g-q6qh-q4v8
- https://nvd.nist.gov/vuln/detail/CVE-2023-49798
- https://github.com/OpenZeppelin/openzeppelin-contracts-upgradeable/commit/31f9fb9d171f60b2271b2b9c6f62d43302bf9489
- https://github.com/OpenZeppelin/openzeppelin-contracts/commit/88ac712e06832bce73b41e8166cded2729e25205
- https://github.com/OpenZeppelin/openzeppelin-contracts
