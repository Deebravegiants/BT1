### Title
ETH Deposit Limit Not Enforced When `totalAssetDeposits` Equals the Limit - (File: contracts/LRTDepositPool.sol)

### Summary
In `LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit`, the ETH branch omits the incoming `amount` from the limit comparison, while the ERC20 branch correctly includes it. This means when `totalAssetDeposits == depositLimit`, an ETH deposit is incorrectly allowed to proceed, bypassing the configured cap.

### Finding Description
`_checkIfDepositAmountExceedesCurrentLimit` contains two branches:

```solidity
// contracts/LRTDepositPool.sol L676-L682
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← `amount` missing
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct
}
```

The ETH branch evaluates `totalAssetDeposits > limit` (strict greater-than, no `amount`). The ERC20 branch evaluates `totalAssetDeposits + amount > limit`. When `totalAssetDeposits == limit`, the ETH branch returns `false` (not exceeded), so `_beforeDeposit` does not revert and the deposit is minted. After the deposit, `totalAssetDeposits` exceeds the configured limit.

This is structurally identical to the reference bug: in a specific conditional branch, the wrong variable (here: the expression without `amount`) is used, causing the guard to silently pass when it should reject.

### Impact Explanation
The ETH deposit cap configured by the admin via `depositLimitByAsset` is not enforced for the boundary case where `totalAssetDeposits == limit`. Any depositor can push ETH deposits beyond the protocol's intended ceiling. The protocol fails to deliver its promised deposit-limit guarantee for ETH, but no funds are directly stolen or frozen.

**Impact: Low — Contract fails to deliver promised returns.**

### Likelihood Explanation
Any unprivileged depositor can call `depositETH` at any time. The condition `totalAssetDeposits == depositLimit` is reachable in normal operation (e.g., the pool fills up to exactly the limit). No special privileges, front-running, or external compromise is required.

**Likelihood: Medium.**

### Recommendation
Include `amount` in the ETH branch, consistent with the ERC20 branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

### Proof of Concept
1. Admin sets `depositLimitByAsset(ETH_TOKEN) = 100 ether`.
2. Protocol accumulates exactly `100 ether` in ETH deposits (`totalAssetDeposits == 100 ether`).
3. Alice calls `depositETH{value: 1 ether}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit` evaluates `100 ether > 100 ether` → `false` → no revert.
5. `_mintRsETH` mints rsETH for Alice; `totalAssetDeposits` is now `101 ether`, exceeding the limit.
6. For comparison, if Alice had deposited an ERC20 token, the check would be `100 ether + 1 ether > 100 ether` → `true` → revert `MaximumDepositLimitReached`. [1](#0-0) [2](#0-1)

### Citations

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
