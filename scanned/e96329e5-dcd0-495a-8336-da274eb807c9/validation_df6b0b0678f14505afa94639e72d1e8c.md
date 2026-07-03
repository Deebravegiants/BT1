### Title
Manager `stakeEthForStETH` Consumes stETH Deposit Capacity, Blocking User `depositAsset(stETH)` - (File: contracts/LRTDepositPool.sol)

### Summary

`LRTDepositPool.stakeEthForStETH` converts ETH held in the pool into stETH via Lido's `submit()`. The resulting stETH balance is immediately counted by `getTotalAssetDeposits(stETH)` against the stETH deposit limit. If the limit is nearly exhausted by prior user deposits, a manager-initiated ETH→stETH conversion can push `getTotalAssetDeposits(stETH)` over the cap, causing all subsequent `depositAsset(stETH, ...)` calls to revert with `MaximumDepositLimitReached`.

### Finding Description

`stakeEthForStETH` is a manager-only function that calls `ILido.submit{value: ethAmount}` and receives stETH tokens directly into the deposit pool: [1](#0-0) 

After the call, the deposit pool's stETH ERC-20 balance increases by approximately `ethAmount`. `getTotalAssetDeposits(stETH)` measures this balance directly: [2](#0-1) 

The deposit limit check in `_checkIfDepositAmountExceedesCurrentLimit` then compares the new (inflated) total against `depositLimitByAsset[stETH]`: [3](#0-2) 

If `getTotalAssetDeposits(stETH)` already exceeds the limit (pushed there by the manager conversion), the check returns `true` for any nonzero `amount`, and `_beforeDeposit` reverts with `MaximumDepositLimitReached`: [4](#0-3) 

There is no guard in `stakeEthForStETH` that checks the remaining stETH deposit headroom before converting. The ETH that was converted was already tracked under the ETH deposit limit (separate accounting), so the conversion effectively double-shifts capacity: ETH headroom is freed while stETH headroom is consumed.

### Impact Explanation

Users who hold stETH and attempt to deposit it via `depositAsset(stETH, ...)` receive a revert. They cannot obtain rsETH for their stETH even though the protocol is designed to accept it. No funds are lost, but the protocol fails to deliver its promised service (stETH → rsETH conversion). This matches the **Low** scope: *contract fails to deliver promised returns, but doesn't lose value*.

### Likelihood Explanation

The scenario requires no adversarial actor. It arises from normal operational use:
1. The stETH deposit limit is set (e.g., 1000 ETH).
2. Users deposit stETH up to near the limit (e.g., 990 ETH worth).
3. The LRT manager, performing routine ETH-yield optimization, calls `stakeEthForStETH(referral, 20 ether)`.
4. `getTotalAssetDeposits(stETH)` becomes ≥ 1010 ETH, exceeding the 1000 ETH limit.
5. All `depositAsset(stETH, ...)` calls revert until the admin raises the limit via `updateAssetDepositLimit`.

The manager role is a trusted but non-admin role; the action is routine and expected. The collision with the deposit limit is a design gap, not a configuration error.

### Recommendation

Before executing the Lido `submit`, check that the resulting stETH balance will not exceed the stETH deposit limit, or — preferably — exclude manager-sourced stETH (obtained via `stakeEthForStETH`) from the deposit-limit accounting by tracking it separately. A simpler mitigation is to add a headroom check inside `stakeEthForStETH`:

```solidity
function stakeEthForStETH(address referral, uint256 ethAmount) external onlyLRTManager {
    address stETHAddress = lrtConfig.getLSTToken(LRTConstants.ST_ETH_TOKEN);
    // Ensure conversion won't exhaust user deposit capacity
    uint256 currentDeposits = getTotalAssetDeposits(stETHAddress);
    uint256 limit = lrtConfig.depositLimitByAsset(stETHAddress);
    require(currentDeposits + ethAmount <= limit, "Would exceed stETH deposit limit");
    uint256 stETHShares = ILido(stETHAddress).submit{ value: ethAmount }(referral);
    emit AssetStaked(stETHAddress, ethAmount, stETHShares);
}
```

### Proof of Concept

```solidity
// Setup
lrtConfig.updateAssetDepositLimit(stETH, 1000e18);

// Pre-fill: simulate 990e18 stETH already in pool
deal(stETH, address(lrtDepositPool), 990e18);

// Manager converts 20 ETH → stETH
vm.deal(address(lrtDepositPool), 20 ether);
vm.prank(manager);
lrtDepositPool.stakeEthForStETH(address(0), 20 ether);

// getTotalAssetDeposits(stETH) is now ~1010e18 > 1000e18
assert(lrtDepositPool.getTotalAssetDeposits(stETH) > 1000e18);

// User deposit reverts
vm.prank(user);
vm.expectRevert(ILRTDepositPool.MaximumDepositLimitReached.selector);
lrtDepositPool.depositAsset(stETH, 1e18, 0, "");
```

The `stakeEthForStETH` function has no deposit-limit guard, `getTotalAssetDeposits` counts all stETH in the pool regardless of origin, and `_checkIfDepositAmountExceedesCurrentLimit` blocks users once the total exceeds the cap. The path is concrete, requires no privileged compromise beyond the expected manager role, and is locally testable on unmodified code.

### Citations

**File:** contracts/LRTDepositPool.sol (L444-444)
```text
        assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));
```

**File:** contracts/LRTDepositPool.sol (L565-571)
```text
    function stakeEthForStETH(address referral, uint256 ethAmount) external onlyLRTManager {
        address stETHAddress = lrtConfig.getLSTToken(LRTConstants.ST_ETH_TOKEN);

        uint256 stETHShares = ILido(stETHAddress).submit{ value: ethAmount }(referral);

        emit AssetStaked(stETHAddress, ethAmount, stETHShares);
    }
```

**File:** contracts/LRTDepositPool.sol (L661-663)
```text
        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }
```

**File:** contracts/LRTDepositPool.sol (L676-682)
```text
    function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (asset == LRTConstants.ETH_TOKEN) {
            return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
        }
        return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
    }
```
