# [M] M-1 Underflow with _coverDeficit()

## Summary
Severity: Medium
Contest weight: 0.1170
Dataset id: 2750
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An attacker can directly transfer tokens to the Umbrella contract, causing an underflow error when Umbrella.setPendingDeficit() or Umbrella.setDeficitOffset() is triggered.  
This happens because the _coverDeficit() function returns the entire contract balance when transferring tokens, rather than just the portion sent by msg.sender, and hacker can increase it by a direct transfer:  
IERC20(aToken).safeTransferFrom(_msgSender(), address(this), amount);  
amount = IERC20(aToken).balanceOf(address(this));  
Umbrella.sol#L148-L151  
Governance has the ability to transfer excess tokens via an emergency function. However, an attacker can frontrun the next call to coverDeficitOffset() and coverPendingDeficit() functions, causing a DoS again.

## Recommendation
We recommend considering the case where the contract already holds funds when calculating the actual received balance.  
2.4 Low
