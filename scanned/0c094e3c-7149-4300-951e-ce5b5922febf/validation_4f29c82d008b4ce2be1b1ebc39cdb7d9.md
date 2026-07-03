### Title
Stale Infinite Approval to Old LRTConverter After Address Update in LRTConfig - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool.maxApproveToLRTConverter()` grants `type(uint256).max` approval to whichever address `lrtConfig.getContract(LRTConstants.LRT_CONVERTER)` returns at call time. The corresponding `revokeApproveToLRTConverter()` also reads the converter address from `lrtConfig` at call time. If the `LRT_CONVERTER` address is ever updated in `LRTConfig`, the old converter contract retains its infinite approval over all LST tokens held by `LRTDepositPool`, and the revoke function silently targets the new converter instead of the old one — leaving the old address permanently approved.

The same pattern exists in `NodeDelegator.sol` for `maxApproveToEigenStrategyManager()` / `revokeApprovalToEigenStrategyManager()` with respect to `lrtConfig.strategyManager()`.

### Finding Description

In `LRTDepositPool.sol`, the manager calls `maxApproveToLRTConverter(asset)` to grant the current converter unlimited spending rights over each supported LST:

```solidity
function maxApproveToLRTConverter(address asset) external onlySupportedERC20Token(asset) onlyLRTManager {
    address lrtConverterAddress = lrtConfig.getContract(LRTConstants.LRT_CONVERTER);
    IERC20(asset).forceApprove(lrtConverterAddress, type(uint256).max);
}
``` [1](#0-0) 

The revoke counterpart reads the same live registry value:

```solidity
function revokeApproveToLRTConverter(address asset) external onlySupportedERC20Token(asset) onlyLRTManager {
    address lrtConverterAddress = lrtConfig.getContract(LRTConstants.LRT_CONVERTER);
    IERC20(asset).forceApprove(lrtConverterAddress, 0);
}
``` [2](#0-1) 

When `LRTConfig` is updated to point `LRT_CONVERTER` to a new implementation:
1. The old converter address still holds `type(uint256).max` allowance from `LRTDepositPool` for every LST that was ever approved.
2. Calling `revokeApproveToLRTConverter()` after the update revokes from the **new** converter, not the old one — the old approval is never cleared.

The identical pattern exists in `NodeDelegator.sol`:

```solidity
function maxApproveToEigenStrategyManager(address asset) external override onlySupportedAsset(asset) onlyLRTManager {
    IERC20(asset).forceApprove(lrtConfig.strategyManager(), type(uint256).max);
}

function revokeApprovalToEigenStrategyManager(address asset) external override onlyLRTManager {
    IERC20(asset).forceApprove(lrtConfig.strategyManager(), 0);
}
``` [3](#0-2) 

Both functions resolve the spender address dynamically from `lrtConfig` at call time, so a stale approval to the old address is irrevocable through the normal interface once the registry is updated.

### Impact Explanation

`LRTDepositPool` is the primary accumulation point for all user-deposited LSTs (stETH, ETHx, etc.) before they are forwarded to `NodeDelegator`. An old `LRTConverter` address with a residual `type(uint256).max` allowance can call `transferFrom(LRTDepositPool, attacker, balance)` for every approved token, draining the entire deposit pool. This constitutes **direct theft of user funds at rest** — Critical severity.

For `NodeDelegator`, the same residual approval over LSTs sitting in the delegator (awaiting `depositAssetIntoStrategy`) enables the same drain path.

### Likelihood Explanation

`LRTConverter` is a protocol-internal upgradeable contract. Protocol upgrades (e.g., replacing `LRTConverter` with a new version) are a routine operational event. The `LRTConfig` registry is explicitly designed to manage and update contract addresses. Every prior call to `maxApproveToLRTConverter` for any supported asset leaves a permanent `type(uint256).max` allowance on the old address. If the old converter implementation contains any exploitable path (reentrancy, misconfigured access control, or a logic bug discovered post-deployment), an attacker can exploit it to invoke `transferFrom` against `LRTDepositPool`. Likelihood is **Medium** — it requires a converter upgrade event combined with a latent bug in the old implementation, but both conditions are plausible in a live protocol.

### Recommendation

1. **Snapshot the old address before updating**: In any `LRTConfig` setter that changes `LRT_CONVERTER` or `strategyManager`, emit an event or store the old address so callers can revoke it.
2. **Accept the old address as a parameter in the revoke functions**: Change `revokeApproveToLRTConverter` and `revokeApprovalToEigenStrategyManager` to accept an explicit `spender` address rather than reading from `lrtConfig`, so the manager can revoke from the old address after an upgrade.
3. **Revoke before updating**: Establish an operational procedure (or enforce it on-chain) that requires revoking all existing approvals before the registry address is changed.

### Proof of Concept

1. Manager calls `maxApproveToLRTConverter(stETH)` → `LRTDepositPool` now has `allowance[LRTDepositPool][OldConverter] = type(uint256).max`.
2. Admin updates `LRTConfig` to point `LRT_CONVERTER` to `NewConverter`.
3. Manager calls `revokeApproveToLRTConverter(stETH)` → this sets `allowance[LRTDepositPool][NewConverter] = 0`. `OldConverter` still has `type(uint256).max`.
4. A vulnerability in `OldConverter` is exploited: attacker calls `OldConverter.exploit()` which internally calls `stETH.transferFrom(LRTDepositPool, attacker, stETH.balanceOf(LRTDepositPool))`.
5. All stETH in `LRTDepositPool` is drained.

### Citations

**File:** contracts/LRTDepositPool.sol (L365-368)
```text
    function maxApproveToLRTConverter(address asset) external onlySupportedERC20Token(asset) onlyLRTManager {
        address lrtConverterAddress = lrtConfig.getContract(LRTConstants.LRT_CONVERTER);
        IERC20(asset).forceApprove(lrtConverterAddress, type(uint256).max);
    }
```

**File:** contracts/LRTDepositPool.sol (L373-376)
```text
    function revokeApproveToLRTConverter(address asset) external onlySupportedERC20Token(asset) onlyLRTManager {
        address lrtConverterAddress = lrtConfig.getContract(LRTConstants.LRT_CONVERTER);
        IERC20(asset).forceApprove(lrtConverterAddress, 0);
    }
```

**File:** contracts/NodeDelegator.sol (L511-528)
```text
    function maxApproveToEigenStrategyManager(address asset)
        external
        override
        onlySupportedAsset(asset)
        onlyLRTManager
    {
        if (asset == LRTConstants.ETH_TOKEN) {
            revert ILRTConfig.AssetNotSupported();
        }
        IERC20(asset).forceApprove(lrtConfig.strategyManager(), type(uint256).max);
    }

    /// @notice Revokes the approval of an asset to the eigen strategy manager
    /// @dev can only b called by the LRT manager
    /// @param asset the asset to revoke approval for
    function revokeApprovalToEigenStrategyManager(address asset) external override onlyLRTManager {
        IERC20(asset).forceApprove(lrtConfig.strategyManager(), 0);
    }
```
