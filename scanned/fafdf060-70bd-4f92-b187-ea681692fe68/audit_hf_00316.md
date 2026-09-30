# [M] Unconstrained fee

## Summary
Severity: Medium
Contest weight: 0.1152
Dataset id: 1563
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[MasterChef.sol#L86-L101](https://github.com/code-423n4/2022-02-concur/blob/main/contracts/MasterChef.sol#L86-L101)  

Token fee in `MasterChef` can be set to more than 100%, (for example, by accident) causing all `deposit` calls to fail due to underflow on subtraction when reward is lowered by the fee, thus breaking essential mechanics. Note that after the fee has been set to any value, it cannot be undone. A token cannot be removed, added, or added the second time. Thus, mistakenly (or deliberately, maliciously) added fee that is larger than 100% will make the contract impossible to recover from not being able to use the token.

## Recommendation
On setting fee ensure that it is below a set maximum, which is set to no more than 100%.

The warden has identified admin privilege that would enable them to set the deposit fee to 100%.  
 The value can also be increased above 100% to cause a denial of service to the user.

 Mitigation would require offering a more appropriate upper limit to the fee.
