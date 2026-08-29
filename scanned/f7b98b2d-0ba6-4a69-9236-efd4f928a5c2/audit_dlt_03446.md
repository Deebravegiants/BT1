# [M] Withdrawals in AccountManager are prone to DOS attacks.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1278
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/accountingManager/AccountingManager.sol#L570-L571


# Vulnerability details

## Impact
Withdrawals can be dossed by an attacker.

## Proof of Concept
The recurrence/likeliness of this attack depends on how close the value of `amountAskedForWithdraw_temp` is to `neededAssets`. But, anyway, if an attacker wants to DOS, he can still do it.

Let's try to make the amount returned by `neededAssetsForWithdraw` function to become smaller.

`neededAssetsForWithdraw` is defined as:

```
    function neededAssetsForWithdraw() public view returns (uint256) {
        uint256 availableAssets = baseToken.balanceOf(address(this)) - depositQueue.totalAWFDeposit;
        if ( // check if the withdraw group is fullfilled
            currentWithdrawGroup.isStarted == false || currentWithdrawGroup.isFullfilled == true
                || availableAssets >= currentWithdrawGroup.totalCBAmount
        ) {
            return 0;
        }
        return currentWithdrawGroup.totalCBAmount - availableAssets;
    }
```
If `availableAssets` is a big value, then `currentWithdrawGroup.totalCBAmount - availableAssets;` is small.

`availableAssets` can be increased when an attacker directly transfers baseToken using ERC20 transfer.

Now, in `retrieveTokensForWithdraw`:

`uint256 neededAssets = neededAssetsForWithdraw();`

and

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-noya-findings/issues/1278_
