# [M] Fees can be any amount

## Summary
Severity: Medium
Contest weight: 0.0978
Dataset id: 1673
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In `transferBribes`, the fees are user input, rather than calculation using `fee` (state var).  
Currently, `fee` is unused: [BribeVault.sol#L23](https://github.com/code-423n4/2022-02-redacted-cartel/blob/main/contracts/BribeVault.sol#L23).  

Therefore the fees amounts might be wrong.

I don’t believe M-14 mentions validation of fees, as such will mark this finding as unique.
 
Ultimately the function trusts the Admin input instead of using the storage variable, giving less security guarantees as to the fairness of the Distribution of the Bribes.
 
Because this is contingent on a malicious admin, I believe medium severity to be appropriate.

## Recommendation
No recommendation
