# [C] Gas allocation error in CALL operations in Besu EVM

## Summary
Severity: Critical
Chain: Ethereum
Component: hyperledger/besu
CVE: CVE-2022-36025
CWE: Unsigned to Signed Conversion Error
Published: 2022-09-23
Source: https://github.com/besu-eth/besu/security/advisories/GHSA-4456-w38r-m53x
Type: github-advisory

## Details
### Impact
An error in 32 bit signed and unsigned types in the calculation of available gas in the CALL operations (including DELEGATECALL) results in incorrect gas being passed into called contracts and incorrect gas being returned after call execution.  Where the amount of gas makes a difference in the success or failure, or if the gas is a negative 64 bit value, the execution will result in a different state root than expected, resulting in a consensus failure in networks with multiple EVM implementations. 

In networks with a single EVM implementation this can be used to execute with significantly more gas than then transaction requested, possibly exceeding gas limitations. 

### Patches
Version 22.7.1 contains a fix, ensuring that excess gas will not be allocated to inner transaction calls and correcting the excess gas errors.

### Workarounds
Reverting to version 22.1.3 or earlier will prevent incorrect execution. However many ethereum mainnet networks require changes in more recent versions of Besu and should not use older versions of besu and should instead use the patched version.  

Ethereum Classic and other networks not depending on a Proof of Stake transition should function fine with version 22.1.3 or earlier.

### References
TBD or delete

### For more information
Issue was found by [Martin Holst Swende](https://github.com/holiman) using [goevmlab](https://github.com/holiman/goevmlab), it is believed that no production networks have transactions that would trigger this failure.
