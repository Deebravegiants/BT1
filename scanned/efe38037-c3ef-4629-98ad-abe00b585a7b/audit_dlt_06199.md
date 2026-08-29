# [M] 2300 gas unit-fixed is not enough for sending Native ETH from the EtherFiNode contract to the Treasury contract via the EtherFiNode#`withdrawFunds()`

## Summary
Severity: Medium
Chain: Smart contract
Component: ether-fi
Published: 2023-11-15
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/54
Type: hats-finding

## Details
**Github username:** @0xmuxyz
**Twitter username:** --
**Submission hash (on-chain):** 0x834c2aefee1a5e8b690e5084d0503016ac1a4cf4d2fa334bb94c4a7eaa27ab4d
**Severity:** medium

**Description:**
## Description
When a full withdrawal, the EtherFiNodesManager#`fullWithdraw()` would be called.

Within the EtherFiNodesManager#`fullWithdraw()`, the EtherFiNodesManager#`_distributePayouts()` would be called like this: \
https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/EtherFiNodesManager.sol#L259
```solidity
    /// @notice process the full withdrawal
    /// @dev This fullWithdrawal is allowed only after it's marked as EXITED.
    /// @dev EtherFi will be monitoring the status of the validator nodes and mark them EXITED if they do;
    /// @dev It is a point of centralization in Phase 1
    /// @param _validatorId the validator Id to withdraw from
    function fullWithdraw(uint256 _validatorId) public nonReentrant whenNotPaused{
        ...
        _distributePayouts(_validatorId, toTreasury, toOperator, toTnft, toBnft); ///<------------------ @audit
        ...
```

When a partial withdrawal to skim rewards, the EtherFiNodesManager#`partialWithdraw()` would be called.

Within the EtherFiNodesManager#`partialWithdraw()`, the EtherFiNodesManager#`_distributePayouts()` would be called as well like this: \
https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/EtherFiNodesManager.sol#L229
```solidity
    /// @notice Process the rewards skimming
    /// @param _validatorId The validator Id
    function partialWithdraw(uint256 _validatorId) public nonReentrant whenNotPaused {
        ...
        _distributePayouts(_validatorId, toTreasury, toOperator, toTnft, toBnft); ///<------------------ @audit
    }
```

Within the EtherFiNodesManager#`_distributePayouts()`, the EtherFiNode#`withdrawFunds()` would be called like this: \
https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/EtherFiNodesManager.sol#L495-L500

_Trimmed to 38 lines — full report: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/54_
