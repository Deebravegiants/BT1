# [M] Short-term freezing of user funds and loss of fees because of insufficient vault connection check

## Summary
Severity: Medium
Chain: Smart contract
Component: Catalyst-Exchange
Published: 2024-02-07
Source: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/87
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x34d7f13ba82833dfea63f42db4785792c97e7ac6b86e5019a1cf3e89be5da470
**Severity:** medium

**Description:**
**Description**\
In order to succesfully do cross-chain swaps (or any other interaction cross-chain), vaults should be connected.

Connection of vaults has to be mutual (vault1 should call setConnection with vault2, and vault2 should call setConnection with vault1).

But in the current implementation of the contract if vault1 called setConnection with vault2, but vault2 didn't do same for vault1:

Users of vault1 can still be able to proceed with swaps(sendAsset/sendLiquidity) between these vaults.

This is because those functions uses the following modifier:
```solidity
    /**
     * @notice Verify a connected pool.
     */ 
    modifier onlyConnectedPool(bytes32 channelId, bytes memory vault) {
        // Only allow connected vaults
        if (!_vaultConnection[channelId][vault]) revert VaultNotConnected();
        _;
    }
```

And _vaultConnection mapping only checks if vault1 is connected to vault2, and doesn't check if vault2 is also connected to vault1.

So users will be able to call these functions and the sending value process will be succesfull from the point of view of vault1. But since vault2 is not connected to vault1, when message send from vault1 to vault2 cross-chain, "receiveAsset()" or "receiveLiquidity()" from vault2 will fail with "vaultNotConnected" error. 

In this process, relayer will periodically try to relay the message but can not be able to do it. When timeOut came, relayer will call "onSendAssetFailure()" or "onSendLiquidityFailure()" functions, and in the end users will get their tokens initially sent, back.

But in this process, users fund will be frozen until timeOut. And also users' paid fees will be lost to nothing.

Let me remind you that this happens because protocol's implementation error, and user is completely innocent when trying to use these functions thinking the vaults are connected.

**Recommendation**\

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/87_
