# [M] Reentrancy Vector In depositEtherToL2()

## Summary
Severity: Medium
Contest weight: 0.1116
Dataset id: 14653
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function depositEtherToL2() does not have the nonReentrant modifier. It is therefore possible to reenter into depositEtherToL2().
Both proposeBlock() and depositEtherToL2() read and write to the fields state.ethDeposits and state.slotA.numEthDeposits and are potential reentrancy vectors.
Additionally, LibDepositing.depositEtherToL2() makes a call to the bridge contract which would allow bypassing the canDepositEthToL2() check. However, the bridge contract implements a receive() function with no code, and so reentrancy is not possible.
The testing team was unable to find, during the allocated time, an exploitable reentrancy vector to negatively impact the contract. Thus, the impact is rated as medium severity.

## Recommendation
Add the nonReentrant modifier to the function depositEtherToL2() in TaikoL1.sol.
