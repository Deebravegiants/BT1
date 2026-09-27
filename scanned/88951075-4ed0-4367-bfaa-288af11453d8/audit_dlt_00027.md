# [H] SHL, SHR, and SAR operations trigger native exception at key values

## Summary
Severity: High
Chain: Ethereum
Component: hyperledger/besu
CVE: CVE-2021-41272
CWE: Integer Coercion Error
Published: 2021-12-10
Source: https://github.com/besu-eth/besu/security/advisories/GHSA-7pg2-p5vj-xp5h
Type: github-advisory

## Details
### Impact
Changes in the implementation of the SHL, SHR, and SAR operations resulted in the introduction of a signed type coercion error in values that represent negative values for 32 bit signed integers.  Smart contracts that ask for shifts between approximately 2 billion and 4 billion bits (nonsensical but valid values for the operation) will fail to execute and hence fail to validate.  

* In networks where vulnerable versions are mining with other clients or non-vulnerable versions this will result in a fork and the relevant transactions will not be included in the fork. 
* In networks where vulnerable versions are not mining (such as Rinkeby) no fork will result and the validator nodes will stop accepting blocks.
* In networks where only vulnerable versions are mining the relevant transaction will not be included in any blocks. When the network adds a non-vulnerable version the network will act as in the first case.

### Patches
Besu 21.10.2 fixes this (PR #3039). Besu 21.7.4 is not vulnerable and clients can roll back to that version.

### Workarounds
Once a transaction with the relevant shift operations is included in the canonical chain the only remediation is to make sure all nodes are on non-vulnerable versions.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Hyperledger Besu](https://github.com/hyperledger/besu/issues)
* Email us at [security@hyperledger.org](mailto:security@hyperledger.org)
