# [M] Improper balanceOf() in TargetVaultDopple/TargetVaultACrypto

## Summary
Severity: Medium
Contest weight: 0.4147
Dataset id: 12055
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In previous sections, we have examined a number of standard APIs, i.e., deposit(), withdraw(), emergencyWithdrawAll(), harvest(), and collectFees(). Next, we examine another commonly-defined function balanceOf(). Note that this function is used to return back the token balance that is being invested in the target vault. To elaborate, we show below the related balanceOf() routine from the TargetVaultDopple contract. It implements a rather straightforward logic in computing the balance of target vault plus deposited balance (line 232). It comes to our attention that availableBalance() returns token balance denominated at the target token for investment, while vaultBalance() returns the share amount held in the staking contract, i.e., doppleStaking. In other words, the share amount needs to properly transformed back to the amount of investment tokens. The same issue is also applicable to another target vault, i.e., TargetVaultACrypto.
```solidity
* @dev Balance of target vault plus deposited balance
function balanceOf() public view virtual returns (uint256) 
    return availableBalance().add(vaultBalance());
```

## Recommendation
Revised the above balanceOf() of affected target vaults to return the right balance.
