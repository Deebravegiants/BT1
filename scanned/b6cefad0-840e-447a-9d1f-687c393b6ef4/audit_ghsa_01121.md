# [M] Denial of Service in ipfs-bitswap

## Summary
Severity: Medium
Advisory: GHSA-6fcr-9h9g-23fq
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-6fcr-9h9g-23fq
Type: github-advisory

## Affected
- npm: `ipfs-bitswap` — affected >=0 <0.24.1

## Details
Versions of `ipfs-bitswap` prior to 0.24.1 are vulnerable to Denial of Service (DoS). The package put unwanted blocks in the blockstore, which could be used to exhaust system resources in specific conditions.


## Recommendation

Upgrade to version 0.24.1 or later.

## References
- https://github.com/ipfs/js-ipfs-bitswap/pull/194
- https://github.com/ipfs/js-ipfs-bitswap
- https://snyk.io/vuln/SNYK-JS-IPFSBITSWAP-174847
- https://www.npmjs.com/advisories/916
