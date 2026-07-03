### Title
ETH Deposit Limit Check Ignores Deposit Amount, Allowing Limit Bypass - (File: contracts/LRTDepositPool.sol)

### Summary
The `_checkIfDepositAmountExceedesCurrentLimit` function in `LRTDepositPool` applies an asymmetric validation: for ERC20 assets it correctly includes the incoming `amount` in the limit comparison, but for ETH it omits `amount` entirely. Any unprivileged depositor can bypass the ETH deposit cap in a single transaction.

### Finding Description
In `LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit`, the ETH branch reads:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
}
return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
```

The ETH path checks only whether the **current** total already exceeds the limit; the incoming `amount` is never added. The ERC20 path correctly evaluates `totalAssetDeposits + amount`. Because `_beforeDeposit` reverts only when this function returns `true`, an ETH deposit of any size is accepted as long as the pre-deposit total is ≤ the configured limit. [1](#0-0) 

The check is invoked unconditionally for every ETH deposit: [2](#0-1) 

The public entry point is permissionless: [3](#0-2) 

### Impact Explanation
The deposit limit is a risk-management control that caps protocol exposure to ETH (e.g., to stay within EigenLayer strategy capacity or TVL targets). Because the check ignores `amount` for ETH, a single depositor can push the ETH TVL arbitrarily above the configured cap in one transaction. This silently violates the protocol's stated invariant and can cause:

- Over-allocation into EigenLayer ETH strategies beyond their intended capacity.
- Inflated rsETH supply relative to the risk budget, degrading the backing ratio for all holders.
- Operational inability to route the excess ETH into strategies, leaving it idle and misaccounted.

**Impact: Low — Contract fails to deliver promised returns (deposit cap guarantee is broken), but deposited funds are not directly lost.**

### Likelihood Explanation
The `depositETH` function is public and requires no role. Any depositor who observes that `totalAssetDeposits ≤ depositLimit` can immediately exploit this by sending a large ETH value. No special conditions, front-running, or privileged access are needed. Likelihood is **High**.

### Recommendation
Include `amount` in the ETH branch, mirroring the ERC20 logic:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
```

Or unify both branches:

```solidity
return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
```

### Proof of Concept
Assume:
- `depositLimitByAsset(ETH_TOKEN) = 1000 ether`
- `getTotalAssetDeposits(ETH_TOKEN) = 900 ether` (below limit)

1. Attacker calls `depositETH{value: 5000 ether}(minRSETH, "")`.
2. `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 5000 ether)` evaluates `900 ether > 1000 ether` → `false`.
3. Deposit proceeds; `getTotalAssetDeposits(ETH_TOKEN)` becomes `5900 ether` — 5.9× the intended cap.
4. Attacker receives rsETH minted at the current rate; the protocol now holds ETH far beyond its risk budget. [1](#0-0)

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

**File:** contracts/LRTDepositPool.sol (L661-669)
```text
        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
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
