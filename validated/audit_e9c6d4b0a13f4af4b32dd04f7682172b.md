The code at lines 676-682 confirms the claim exactly. The ETH branch at line 679 uses `totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)` (ignoring `amount`), while the ERC20 branch at line 681 correctly uses `totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)`. The call path through `depositETH` → `_beforeDeposit` → `_checkIfDepositAmountExceedesCurrentLimit` is confirmed. The finding is valid.

---

Audit Report

## Title
ETH Deposit Limit Check Ignores Deposit Amount, Allowing Limit Bypass - (File: contracts/LRTDepositPool.sol)

## Summary
`_checkIfDepositAmountExceedesCurrentLimit` uses an asymmetric check for ETH versus ERC20 assets: the ETH branch tests only whether the current total already exceeds the limit, silently discarding the incoming `amount`. As a result, any depositor can push the protocol's ETH holdings arbitrarily above the configured cap in a single permissionless call.

## Finding Description
In `contracts/LRTDepositPool.sol` at lines 676–682:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // amount ignored
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // correct
}
```

For ERC20 assets the guard is `totalAssetDeposits + amount > limit`, which correctly blocks a deposit that would push the running total over the cap. For ETH the guard is `totalAssetDeposits > limit`, which only tests whether the total **already** exceeds the limit before the deposit lands. The `amount` argument is never incorporated.

The reachable call path is:
- `depositETH` (L76–93) — public, payable, permissionless
- → `_beforeDeposit` (L648–670) — passes `msg.value` as `depositAmount`
- → `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, depositAmount)` (L661) — `depositAmount` is ignored in the ETH branch

No existing check compensates for this omission. `_beforeDeposit` only reverts if `_checkIfDepositAmountExceedesCurrentLimit` returns `true`, which it never does for ETH as long as the pre-deposit total is at or below the limit.

## Impact Explanation
The ETH deposit limit (`depositLimitByAsset`) is the protocol's primary risk-management cap on ETH exposure. Because the cap is never enforced against the incoming amount, the invariant `getTotalAssetDeposits(ETH) ≤ depositLimitByAsset(ETH)` can be violated in a single transaction. The protocol fails to deliver its promised deposit-cap guarantee for ETH. No funds are directly stolen or permanently frozen, placing this squarely in the **Low — Contract fails to deliver promised returns** impact class.

## Likelihood Explanation
The entry point is the public, permissionless `depositETH` function. No special role, flash loan, price manipulation, or victim mistake is required. The only precondition is that the current ETH total has not yet crossed the limit (the normal operating state). Any depositor with sufficient ETH can exceed the cap in a single transaction, and the condition is repeatable. Likelihood is **High**.

## Recommendation
Remove the ETH-specific branch and apply the same amount-inclusive check uniformly:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

This unifies the logic and correctly prevents any single deposit — ETH or ERC20 — from pushing the running total above the configured limit.

## Proof of Concept
Precondition: `depositLimitByAsset(ETH) = 1000 ether`, `getTotalAssetDeposits(ETH) = 999 ether`.

1. Attacker calls `depositETH{value: 10_000 ether}(0, "")`.
2. `_checkIfDepositAmountExceedesCurrentLimit(ETH, 10_000 ether)` evaluates `999 ether > 1000 ether` → `false`.
3. `_beforeDeposit` does not revert; `_mintRsETH` mints rsETH for the full 10,000 ETH.
4. `getTotalAssetDeposits(ETH)` is now 10,999 ETH — ~11× the intended cap.

**Foundry test plan:**
```solidity
function test_ethDepositLimitBypass() public {
    // set limit to 1000 ether, seed pool with 999 ether of prior deposits
    vm.deal(attacker, 10_000 ether);
    vm.prank(attacker);
    depositPool.depositETH{value: 10_000 ether}(0, "");
    assertGt(depositPool.getTotalAssetDeposits(ETH_TOKEN),
             lrtConfig.depositLimitByAsset(ETH_TOKEN));
}
``` [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/LRTDepositPool.sol (L76-93)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
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
