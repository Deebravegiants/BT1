# [H] Improper Initialization in OpenZeppelin

## Summary
Severity: High
Advisory: GHSA-88g8-f5mf-f5rj
CVE: CVE-2021-46320
CWE: CWE-665
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-02-05
Source: https://github.com/advisories/GHSA-88g8-f5mf-f5rj
Type: github-advisory

## Affected
- npm: `@openzeppelin/contracts` — affected >=0 <4.4.1

## Details
In OpenZeppelin <=v4.4.0, initializer functions that are invoked separate from contract creation (the most prominent example being minimal proxies) may be reentered if they make an untrusted non-view external call. Once an initializer has finished running it can never be re-executed. However, an exception put in place to support multiple inheritance made reentrancy possible, breaking the expectation that there is a single execution.

## References
- https://github.com/OpenZeppelin/openzeppelin-contracts/security/advisories/GHSA-9c22-pwxw-p6hx
- https://nvd.nist.gov/vuln/detail/CVE-2021-46320
- https://github.com/OpenZeppelin/openzeppelin-contracts/pull/3006
- https://github.com/OpenZeppelin/openzeppelin-contracts
- https://github.com/OpenZeppelin/openzeppelin-contracts/releases/tag/v4.4.1
