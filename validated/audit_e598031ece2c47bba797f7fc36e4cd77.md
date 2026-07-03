### Title
ETH Deposit Limit Check Missing Deposit Amount Allows Cap Bypass - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit()` applies an asymmetric check for ETH versus LST assets. For LSTs it correctly tests `totalAssetDeposits + amount > depositLimit`, but for ETH it only tests `totalAssetDeposits > depositLimit`, omitting the incoming deposit amount. When the running total is exactly equal to the configured limit the check returns `false`, allowing the deposit to proceed and push the protocol above its own cap.

### Finding Description
`_checkIfDepositAmountExceedesCurrentLimit` is the sole gate that enforces `depositLimitByAsset` for ETH deposits:

```solidity
// contracts/LRTDepositPool.sol  lines 676-682
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← missing `+ amount`
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

The three-state behaviour for ETH:

| `totalAssetDeposits` vs `depositLimit` | Return value | Deposit allowed? |
|---|---|---|
| `< depositLimit` | `false` | ✓ correct |
| `== depositLimit` | `false` | ✗ **wrong** – should be blocked |
| `> depositLimit` | `true` | ✓ correct |

The view helper `getAssetCurrentLimit` already returns `0` when `totalAssetDeposits == depositLimit`, confirming the protocol considers the cap reached, yet `_checkIfDepositAmountExceedesCurrentLimit` still permits the next ETH deposit.

The analog to the reported royalty bug is exact: both are limit-check miscalculations where the validation omits a relevant quantity (the royalty bug omits the collector's existing share; this bug omits the incoming deposit amount), causing the guard to pass when it should reject.

### Impact Explanation
Any depositor can call `depositETH()` when `totalAssetDeposits == depositLimit` and deposit an arbitrarily large amount of ETH. The deposit succeeds, minting rsETH and pushing the protocol's ETH holdings above the configured cap. After this single over-limit deposit, `totalAssetDeposits > depositLimit` and subsequent deposits are correctly blocked. The deposit limit is a risk-management parameter (e.g., capping EigenLayer exposure); bypassing it violates the protocol's stated invariant. No funds are directly stolen, but the protocol takes on more ETH exposure than intended.

**Impact: Low** — Contract fails to deliver promised returns (deposit cap enforcement) but does not lose value.

### Likelihood Explanation
The condition `totalAssetDeposits == depositLimit` is reachable in normal operation: the limit is a round number set by governance, and deposits accumulate toward it over time. Any depositor who monitors on-chain state can observe the exact moment the total reaches the limit and submit a deposit before the next block. No special privileges are required; `depositETH()` is a public payable function.

### Recommendation
Add the deposit amount to the ETH branch, matching the LST branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

### Proof of Concept
1. Governance sets `depositLimitByAsset[ETH_TOKEN] = 10_000 ether`.
2. Over time, `getTotalAssetDeposits(ETH_TOKEN)` reaches exactly `10_000 ether`.
3. `getAssetCurrentLimit(ETH_TOKEN)` returns `0` — the cap is considered full.
4. Attacker calls `depositETH{value: 500 ether}(0, "")`.
5. `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 500 ether)` evaluates `10_000 ether > 10_000 ether` → `false` → no revert.
6. `_mintRsETH` mints rsETH for the attacker; `totalAssetDeposits` becomes `10_500 ether`, 5 % above the configured cap. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/LRTDepositPool.sol (L399-409)
```text
    /// @notice gets the current limit of asset deposit
    /// @param asset Asset address
    /// @return currentLimit Current limit of asset deposit
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
