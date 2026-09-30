# [C] Wrong tokensToCheck logic in BaseRouter enables attackers to steal funds

## Summary
Severity: Critical
Contest weight: 0.2793
Dataset id: 8206
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The BaseRouter implements a mechanism to prevent tokens from being stuck that checks the balance of the router before and after the actions and ensures it remains equal. Problem is, the _addTokenToList(...) function has a bug such that only the last token interacted with is added to the array at the first element (0). The _isInTokenList(...) function returns index 0 if the token is not in the array, so the position uint256 position = index == 0 ? index : index + 1; will always be 0. Attackers can use this to steal other users by waiting for withdraw approvals for the BaseRouter of other users and then use these approvals to withdraw to the BaseRouter, followed by a deposit action in another vault to remove the asset of the withdraw from the tokensToCheck array. The asset is then held by the BaseRouter, which can be retrieved in a following transaction by the attacker by
1) depositing the funds to the vault, where the receiver and owner are the BaseRouter.
2) withdrawing these funds to the attacker, where the receiver is the attacker and the owner the BaseRouter.
3) depositing another asset to another vault, removing the first asset from the tokensToCheck array.

## Proof of Concept
no poc/POCWrongTokensToCheckLogic.t.sol#L80/POCWrongTokensToCheckLogic.t.sol#L80

## Recommendation
Recommendation not found
