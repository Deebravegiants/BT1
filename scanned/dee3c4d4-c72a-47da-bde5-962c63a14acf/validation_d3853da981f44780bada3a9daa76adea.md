### Title
`LRTOracle` calls `LRTDepositPool::pause`, `LRTWithdrawalManager::pause`, and `RSETH::mint` without holding the required roles, making auto-pause and fee-minting permanently broken - (File: contracts/LRTOracle.sol)

### Summary

`LRTOracle._updateRsETHPrice()` is designed to (a) mint protocol fees via `RSETH.mint()` and (b) auto-pause `LRTDepositPool` and `LRTWithdrawalManager` when the rsETH price drops beyond a configured threshold. Both operations require `LRTOracle` to hold `MINTER_ROLE` and `PAUSER_ROLE` respectively inside `LRTConfig`. The access control on the target functions enforces these roles against `msg.sender`, which is `LRTOracle` when the calls are made. There is no mechanism in the code that ensures these roles are granted to `LRTOracle`, and the target functions do not account for `LRTOracle` as an authorized caller by design. If the roles are absent, every price update that generates fees or triggers the downside-protection auto-pause will revert, permanently breaking both mechanisms.

### Finding Description

`LRTOracle._updateRsETHPrice()` contains two cross-contract call paths that require `LRTOracle` to hold specific roles in `LRTConfig`:

**Path 1 – Fee minting:** [1](#0-0) 

`RSETH.mint()` is guarded by: [2](#0-1) 

When `LRTOracle` calls `RSETH.mint()`, `msg.sender` is `LRTOracle`. The `onlyRole(LRTConstants.MINTER_ROLE)` modifier in `LRTConfigRoleChecker` checks `IAccessControl(address(lrtConfig)).hasRole(MINTER_ROLE, msg.sender)`: [3](#0-2) 

If `LRTOracle` does not hold `MINTER_ROLE`, the call reverts and the entire price update fails.

**Path 2 – Auto-pause on price drop:** [4](#0-3) 

`LRTDepositPool.pause()` and `LRTWithdrawalManager.pause()` are both guarded by `onlyRole(LRTConstants.PAUSER_ROLE)`: [5](#0-4) [6](#0-5) 

When `LRTOracle` calls these functions, `msg.sender` is `LRTOracle`. If `LRTOracle` does not hold `PAUSER_ROLE`, both calls revert, the auto-pause never executes, and `_pause()` on `LRTOracle` itself is never reached.

### Impact Explanation

**Fee minting broken:** Any price update that accrues protocol fees will revert. The rsETH price cannot be updated whenever `protocolFeeInETH > 0`, causing the price oracle to stall and the protocol to operate on a stale price. This constitutes a temporary freezing of the price-update mechanism and theft of unclaimed yield (protocol fees are never minted).

**Auto-pause broken:** When the rsETH price drops beyond `pricePercentageLimit`, the downside-protection branch tries to pause `LRTDepositPool` and `LRTWithdrawalManager`. If `LRTOracle` lacks `PAUSER_ROLE`, these calls revert, the entire `updateRSETHPrice()` call reverts, and the protocol is neither paused nor price-updated. Users can continue depositing and withdrawing at a stale (inflated) price, leading to fund loss.

### Likelihood Explanation

`MINTER_ROLE` is typically granted only to `LRTDepositPool` (the user-facing deposit contract). `PAUSER_ROLE` is typically granted to human operator addresses. Neither role is naturally associated with `LRTOracle`. The code provides no `initialize`-time grant of these roles to `LRTOracle`, and no documentation or comment in the contract mandates it. A deployment that omits these grants — which is the natural default — silently breaks both mechanisms. The public `updateRSETHPrice()` function can be called by any external actor, making the failure immediately observable.

### Recommendation

Grant `MINTER_ROLE` and `PAUSER_ROLE` to `LRTOracle` in `LRTConfig` during deployment, **or** refactor the access control on `RSETH.mint()`, `LRTDepositPool.pause()`, and `LRTWithdrawalManager.pause()` to also accept `LRTOracle` as an authorized caller (analogous to adding `onlyMinter` alongside `onlyOwner` in the referenced report). The safest approach is to add an explicit role check or a dedicated modifier (e.g., `onlyLRTOracle`) on the target functions, mirroring the pattern already used for `onlyLRTNodeDelegator` in `LRTUnstakingVault`: [7](#0-6) 

### Proof of Concept

1. Deploy `LRTConfig`, `RSETH`, `LRTDepositPool`, `LRTWithdrawalManager`, and `LRTOracle` without granting `MINTER_ROLE` or `PAUSER_ROLE` to `LRTOracle` (the natural default).
2. Set `protocolFeeInBPS > 0` in `LRTConfig` and allow TVL to grow so `protocolFeeInETH > 0`.
3. Call `LRTOracle.updateRSETHPrice()`.
4. The call reverts at `IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee)` with `CallerNotLRTConfigAllowedRole` because `LRTOracle` lacks `MINTER_ROLE`.
5. Separately, set `pricePercentageLimit` and simulate a price drop beyond the threshold.
6. Call `LRTOracle.updateRSETHPrice()`.
7. The call reverts at `lrtDepositPool.pause()` with `CallerNotLRTConfigAllowedRole` because `LRTOracle` lacks `PAUSER_ROLE`. The protocol is not paused and the price is not updated.

### Citations

**File:** contracts/LRTOracle.sol (L277-282)
```text
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }
```

**File:** contracts/LRTOracle.sol (L304-308)
```text
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
            }
```

**File:** contracts/RSETH.sol (L229-234)
```text
    function mint(
        address to,
        uint256 amount
    )
        external
        onlyRole(LRTConstants.MINTER_ROLE)
```

**File:** contracts/utils/LRTConfigRoleChecker.sol (L19-25)
```text
    modifier onlyRole(bytes32 role) {
        if (!IAccessControl(address(lrtConfig)).hasRole(role, msg.sender)) {
            string memory roleStr = string(abi.encodePacked(role));
            revert ILRTConfig.CallerNotLRTConfigAllowedRole(roleStr);
        }
        _;
    }
```

**File:** contracts/LRTDepositPool.sol (L349-351)
```text
    function pause() external onlyRole(LRTConstants.PAUSER_ROLE) {
        _pause();
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L347-349)
```text
    function pause() external onlyRole(LRTConstants.PAUSER_ROLE) {
        _pause();
    }
```

**File:** contracts/LRTUnstakingVault.sol (L45-52)
```text
    modifier onlyLRTNodeDelegator() {
        ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));

        if (lrtDepositPool.isNodeDelegator(msg.sender) != 1) {
            revert CallerNotLRTNodeDelegator();
        }
        _;
    }
```
