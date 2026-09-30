# [C] UsersCanNotWithdrawTheirDepositsUsingforceUnstakeAll() Function

## Summary
Severity: Critical
Contest weight: 0.2576
Dataset id: 13732
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function forceUnstakeAll() is meant to send the whole stake balance to the user but instead, it attempts to transfer the funds from the user’s account to the Portal contract. In the best case, this means that the user cannot withdraw their stake via the forceUnstakeAll() method and the transaction will fail in most cases. In the worst case, however, the user can first set an allowance for the Portal that equals or exceeds their staked position and subsequently call forceUnstakeAll(). If the user has a sufficient amount in their wallet, the function will then transfer additional funds, corresponding to the staked amount, from the user’s wallet to the Portal contract and, at the same time, reduce the totalPrincipalStaked by the staked amount so that totalPrincipalStaked will no longer reflect the correct value of the total principal staked in the portal. This sequence of actions not only poses a risk of unintentional loss of funds for regular users but also provides a direct path for a malicious actor to manipulate the internal accounting of the portal.

## Recommendation
safeTransfer() should be used instead of safeTransferFrom() as follows:
- IERC20(principalToken).safeTransferFrom(msg.sender, address(this), balance);
+ IERC20(principalToken).safeTransfer(msg.sender, balance);
