# [M] Centralization risk: Owner can steal all earned positive net income from the Vault and deny users from withdrawing.

## Summary
Severity: Medium
Reporter: seyni
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L98
Type: audit-issue

## Details
# Centralization risk: Owner can steal all earned positive net income from the Vault and deny users from withdrawing.

## Summary
Owner can set the `performanceFee64x64` and `withdrawalFee64x64` to 100%, set himself as `feeRecipient` and `keeper` and collect all earned positive income from the Vault when initializing a new epoch using `VaultAdmin.initializeEpoch` as well as potentially denying users from withdrawing.

## Vulnerability Detail
Owner can set `performanceFee64x64` as high as 100% using `VaultAdmin.setPerformanceFee64x64`.
```solidity
        require(newPerformanceFee64x64 < ONE_64x64, "fee > 1");
```
Owner can set `withdrawalFee64x64` as high as 100% using `VaultAdmin.setWithdrawalFee64x64`.

```solidity
        require(newWithdrawalFee64x64 < ONE_64x64, "fee > 1");
```
Owner can set himself as `feeRecipient` using `VaultAdmin.setFeeRecipient`.
```solidity
    function setFeeRecipient(address newFeeRecipient) external onlyOwner {
        VaultStorage.Layout storage l = VaultStorage.layout();
        require(newFeeRecipient != address(0), "address not provided");
        require(newFeeRecipient != l.feeRecipient, "new address equals old");


        emit FeeRecipientSet(
            l.epoch,
            l.feeRecipient,
            newFeeRecipient,
            msg.sender
        );


        l.feeRecipient = newFeeRecipient;
```
Owner can set himself as `keeper` using `VaultAdmin.setKeeper`.
```solidity
    function setKeeper(address newKeeper) external onlyOwner {
        VaultStorage.Layout storage l = VaultStorage.layout();
        require(newKeeper != address(0), "address not provided");
        require(newKeeper != address(l.keeper), "new address equals old");


        emit KeeperSet(l.epoch, l.keeper, newKeeper, msg.sender);


        l.keeper = newKeeper;
    }
```

The fact that the owner has the right to modify these parameters would be fine if it wasn't possible to set such extreme values. The ability of the owner to set very high performance and withdrawal fees (up to 100%) could lead to stolen or stuck users funds if a malicious owner decided to change them, especially if it was done right before a new epoch.

## Impact
The owner can:
- Collect all earned positive income from the Vault when initializing a new epoch using `VaultAdmin.initializeEpoch`.
- Deny users the possibility to withdraw because the `withdrawalFee64x64` is set to 100%. 

In addition to this, potential users could decide not to use the protocol upon seeing that their funds are at risk.

## Code Snippet

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L98

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L116

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L155

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L175

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L234

## Tool used

Manual Review

## Recommendation

Set reasonable maximum values for `performanceFee64x64` and `withdrawalFee64x64`.
