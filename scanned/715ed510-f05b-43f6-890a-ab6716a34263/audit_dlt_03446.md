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

```
        if (amountAskedForWithdraw_temp > neededAssets) {
            revert NoyaAccounting_INVALID_AMOUNT();
        }
```

So, if neededAssets is small enough then this function will revert. 

An attacker sees `retrieveTokensForWithdraw` function by the manager in the mempool. He front runs this transaction by directly transferring baseToken using ERC20 transfer. The amount to be transferred depends on what needs to be done to make `neededAssets` small enough for the function to revert. The attacker can DOS this function as long as they want. This will be critical as it will affect the users' ability to withdraw tokens.

Some things to take note of -

1. One important point to consider is how close the value of `amountAskedForWithdraw_temp` is to the value of `neededAssets` in `retrieveTokensForWithdraw` function. It can be assumed that the value the manager uses for `withdrawAmount` in his `RetrieveData` input will be either equal to `neededAssets` (`neededAssetsForWithdraw()`) or close to it. This is clear from the following comments in the code -

```solidity
    /// @notice if the withdraw group is not fullfilled, we can get the needed assets for the withdraw using this function

    function neededAssetsForWithdraw() public view returns (uint256) {
```

The comment suggests that the manager will use the `needAssetsForWithdraw` function to know how much amount they need to give as input for withdraws in the `retrieveTokensForWithdraw` function. So, the amount that the attacker transfers need not be much. This would make it easier for him to repeatedly carry out the attack.

2. As long as it is viable for the attacker, he will keep doing so. The impact of the dos would be high. As it essentially prevents the users from taking their deposits back as long as the attacker keeps dossing. So, withdrawals will be affected. We know that the protocol has given special emphasis to emergencies. They have a dedicated role that acts during emergencies. Notice the use of `emergencyManager` manager above -

```solidity
    modifier onlyManager() {
        (,,, address keeperContract,, address emergencyManager) = registry.getGovernanceAddresses(vaultId);
        if (!(msg.sender == keeperContract || msg.sender == emergencyManager || msg.sender == registry.flashLoan())) {
            revert NoyaGovernance_Unauthorized(msg.sender);
        }
        _;
    }
```
So, in emergency scenarios when the `emergencyManager` is trying to withdraw tokens. Malicious actors can keep dossing the withdrawals.

## Tools Used
Manual review

## Recommended Mitigation Steps
A possible mitigation could be to entirely remove this check -

```
        if (amountAskedForWithdraw_temp > neededAssets) {
            revert NoyaAccounting_INVALID_AMOUNT();
        }
```
 
Even if the amount `amountAskedForWithdraw_temp` is greater than `neededAssets`, instead of reverting, send the additional tokens back to the connectors.


## Assessed type

DoS
