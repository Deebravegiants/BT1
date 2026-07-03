Audit Report

## Title
ETH Deposit Limit Check Omits Incoming Amount, Allowing Deposits Beyond Configured Cap - (File: contracts/LRTDepositPool.sol)

## Summary
`LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit` applies an asymmetric comparison for ETH vs. ERC-20 assets. The ETH branch tests only `totalAssetDeposits > depositLimit`, omitting the incoming `amount`, while the ERC-20 branch correctly tests `totalAssetDeposits + amount > depositLimit`. Any unprivileged caller can deposit arbitrary ETH beyond the configured cap whenever `totalAssetDeposits <= depositLimit`.

## Finding Description
In `_checkIfDepositAmountExceedesCurrentLimit` at [1](#0-0) , the ETH branch returns `false` (no limit exceeded) whenever `totalAssetDeposits <= depositLimit`, regardless of the size of `amount`. The ERC-20 path at the same function correctly adds `amount` to `totalAssetDeposits` before comparing.

The call chain is: `depositETH` [2](#0-1)  passes `msg.value` as `depositAmount` to `_beforeDeposit`, which calls `_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)` at [3](#0-2) . No other guard in `_beforeDeposit` enforces the deposit cap. [4](#0-3) 

The companion view `getAssetCurrentLimit` correctly computes remaining capacity as `depositLimit - totalAssetDeposits` [5](#0-4) , but this value is never used in the enforcement path for ETH.

## Impact Explanation
`depositLimitByAsset[ETH_TOKEN]` is the protocol's primary risk-management ceiling on ETH exposure. Bypassing it allows any depositor to push ETH TVL arbitrarily above the intended cap. The direct, in-protocol impact is that the contract fails to enforce its promised deposit limit — rsETH is minted against ETH holdings that exceed the protocol's configured risk parameters. This matches the allowed impact: **Low — Contract fails to deliver promised returns**.

## Likelihood Explanation
The entry point `depositETH` is fully permissionless and payable. [6](#0-5)  The only precondition is that `totalAssetDeposits <= depositLimit`, which is the normal operating state of a pool that has not yet been exceeded. No special role, front-running, or external dependency is required. The condition is trivially met and the exploit is repeatable.

## Recommendation
Remove the ETH-specific branch and apply the same `+ amount` logic uniformly:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

## Proof of Concept
1. Admin sets `depositLimitByAsset[ETH_TOKEN] = 1000 ether`.
2. Protocol accumulates `totalAssetDeposits(ETH) = 999 ether` through normal deposits.
3. Attacker calls `depositETH{value: 10_000 ether}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 10_000 ether)` evaluates `999 ether > 1000 ether` → `false` → no revert.
5. 10,000 ETH is accepted, rsETH is minted, and the deposit cap is bypassed by ~10×.

**Foundry test sketch:**
```solidity
function test_ethDepositBypassesLimit() public {
    uint256 cap = 1000 ether;
    lrtConfig.setDepositLimitByAsset(ETH_TOKEN, cap);
    // fill pool to just below cap
    vm.deal(alice, cap - 1 ether);
    vm.prank(alice); depositPool.depositETH{value: cap - 1 ether}(0, "");
    // now deposit far beyond remaining capacity
    vm.deal(attacker, 10_000 ether);
    vm.prank(attacker);
    depositPool.depositETH{value: 10_000 ether}(0, ""); // must not revert to confirm bug
    assertGt(depositPool.getTotalAssetDeposits(ETH_TOKEN), cap);
}
```

### Citations

**File:** contracts/LRTDepositPool.sol (L80-85)
```text
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
```

**File:** contracts/LRTDepositPool.sol (L87-87)
```text
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);
```

**File:** contracts/LRTDepositPool.sol (L402-409)
```text
    function getAssetCurrentLimit(address asset) public view override returns (uint256) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)) {
            return 0;
        }

        return lrtConfig.depositLimitByAsset(asset) - totalAssetDeposits;
    }
```

**File:** contracts/LRTDepositPool.sol (L648-670)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
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
