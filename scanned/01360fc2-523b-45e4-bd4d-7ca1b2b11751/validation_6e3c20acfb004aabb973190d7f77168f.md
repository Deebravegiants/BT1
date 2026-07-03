### Title
ETH Deposit Limit Bypass Due to Missing `amount` in Cap Check - (File: contracts/LRTDepositPool.sol)

### Summary
`_checkIfDepositAmountExceedesCurrentLimit` applies an asymmetric check for ETH versus ERC-20 assets. For ERC-20 tokens the incoming `amount` is included in the comparison, but for ETH it is silently omitted, so the deposit cap can be exceeded by an arbitrary amount in a single transaction.

### Finding Description
`_checkIfDepositAmountExceedesCurrentLimit` branches on the asset type:

```solidity
// ERC-20 path — correctly includes amount
return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));

// ETH path — amount is absent
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
}
``` [1](#0-0) 

The ETH branch only asks "has the limit already been exceeded?" rather than "would this deposit exceed the limit?". Consequently, as long as `totalAssetDeposits ≤ depositLimit` at the moment of the call, the check returns `false` (not exceeded) regardless of how large `msg.value` is.

`depositETH` feeds `msg.value` as `depositAmount` into `_beforeDeposit`, which calls this function: [2](#0-1) [3](#0-2) 

### Impact Explanation
Any depositor can push the protocol's total ETH holdings arbitrarily above the configured `depositLimitByAsset` cap in a single call. The cap is a risk-management control (e.g., limiting EigenLayer slashing exposure or liquidity risk). Bypassing it means the protocol silently accepts more ETH than operators intended, violating the invariant the cap is meant to enforce.

**Impact: Low** — Contract fails to deliver the promised deposit-cap guarantee; no direct fund loss, but the risk-management boundary is broken.

### Likelihood Explanation
Any unprivileged depositor can trigger this at any time by calling `depositETH` with a large `msg.value` when the pool is below its limit. No special conditions or coordination are required.

### Recommendation
Include `depositAmount` in the ETH branch, mirroring the ERC-20 path:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

### Proof of Concept
1. Admin sets `depositLimitByAsset[ETH_TOKEN] = 1000 ether`.
2. Current `getTotalAssetDeposits(ETH_TOKEN)` returns `999 ether`.
3. Attacker calls `depositETH{value: 5000 ether}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit` evaluates `999 ether > 1000 ether` → `false` → check passes.
5. `_mintRsETH` mints rsETH for the full 5000 ETH deposit; the pool now holds 5999 ETH against a 1000 ETH cap.

### Citations

**File:** contracts/LRTDepositPool.sol (L86-93)
```text
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
