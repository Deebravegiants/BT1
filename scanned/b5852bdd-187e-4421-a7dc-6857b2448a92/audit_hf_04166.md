# [C] C-01 | Claiming Yield DoS

## Summary
Severity: Critical
Contest weight: 0.1674
Dataset id: 20847
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The BlastMagicLP and BlastOnboarding contracts do not expect to hold native Ether and therefore will not accrue claimable native ether yield, however they still attempt to claim native yield with the BlastYields.claimAllNativeYields function. The implementation of the BLAST_YIELD contract in go reverts if there is not any claimable Ether: [https://github.com/blast-io/blast/blob/c39cdf1fa7ef9e0d4eaf64a7a5cf7b3c46c739fd/blast-geth/core/vm/contracts.go#L1239](https://github.com/blast-io/blast/blob/c39cdf1fa7ef9e0d4eaf64a7a5cf7b3c46c739fd/blast-geth/core/vm/contracts.go#L1239)

## Recommendation
Either do not invoke the claimAllNativeYields function if there is no native yield to be claimed, or separate the yield claiming logic into independent functions for each type of yield.
