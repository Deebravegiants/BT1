### Title
ETH Deposit Limit Check Omits Current Deposit Amount, Allowing Limit Bypass - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit` applies the ETH deposit cap by checking only the pre-deposit total (`totalAssetDeposits > limit`) while the ERC20 branch correctly checks the post-deposit total (`totalAssetDeposits + amount > limit`). Any unprivileged depositor can therefore exceed the ETH cap by an arbitrary amount in a single call.

### Finding Description
`_checkIfDepositAmountExceedesCurrentLimit` contains an asymmetric check:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)); // ← amount not included
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct
}
```

For ETH the function returns `true` (i.e., "limit exceeded → revert") only when the pre-deposit total already exceeds the cap. The incoming `amount` is never added. Consequently, as long as `totalAssetDeposits ≤ depositLimitByAsset`, the check always passes regardless of how large `amount` is. The public `depositETH` function carries no role restriction and calls `_beforeDeposit`, which calls this check. [1](#0-0) [2](#0-1) 

### Impact Explanation
**Low – Contract fails to deliver promised returns, but doesn't lose value.**

The ETH deposit cap is a risk-management control. Bypassing it allows the protocol to absorb an unbounded amount of ETH in a single block, violating the invariant that `getTotalAssetDeposits(ETH) ≤ depositLimitByAsset(ETH)`. No user funds are stolen and no funds are frozen, but the protocol operates outside its declared safety envelope. [1](#0-0) 

### Likelihood Explanation
**Medium.** The entry point `depositETH` is permissionless (no role guard, only `whenNotPaused` and `onlySupportedAsset`). The bypass requires nothing more than sending ETH while the running total is at or below the cap, a condition that is trivially observable on-chain and routinely true during normal operation. [2](#0-1) 

### Recommendation
Add `amount` to the ETH branch so it mirrors the ERC20 branch:

```diff
 if (asset == LRTConstants.ETH_TOKEN) {
-    return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
+    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
 }
``` [1](#0-0) 

### Proof of Concept
1. Admin sets `depositLimitByAsset(ETH) = 1 000 ETH`.
2. Protocol accumulates `totalAssetDeposits(ETH) = 999 ETH` through normal usage.
3. Attacker calls `depositETH{value: 5 000 ETH}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit` evaluates `999 ETH > 1 000 ETH` → `false` → no revert.
5. `_mintRsETH` mints rsETH for the full 5 000 ETH.
6. `totalAssetDeposits(ETH)` is now 5 999 ETH — nearly 6× the intended cap — with no protocol-level rejection. [3](#0-2) [1](#0-0)

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
