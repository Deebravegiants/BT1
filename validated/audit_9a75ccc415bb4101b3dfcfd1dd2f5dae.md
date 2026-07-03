Audit Report

## Title
ETH Deposit Limit Bypass Due to Missing `amount` in Limit Check — (File: contracts/LRTDepositPool.sol)

## Summary
`_checkIfDepositAmountExceedesCurrentLimit` uses an asymmetric condition: for ERC-20 assets it tests `totalAssetDeposits + amount > depositLimit`, but for ETH it tests only `totalAssetDeposits > depositLimit`, omitting the incoming deposit amount. This allows any depositor to push ETH holdings arbitrarily beyond the configured cap in a single transaction, violating the protocol's core deposit-limit invariant.

## Finding Description
In `LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit` ( [1](#0-0) ):

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));  // ← amount omitted
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

The ETH branch evaluates whether the **current** total already exceeds the limit, not whether the **post-deposit** total would. As long as `totalAssetDeposits ≤ depositLimit`, the function returns `false` regardless of how large `amount` is.

`_beforeDeposit` calls this function and reverts with `MaximumDepositLimitReached` only when it returns `true` ( [2](#0-1) ). Because the ETH branch never accounts for the incoming `amount`, the guard is silently bypassed for all ETH deposits as long as the pool is not already over-limit.

The public entry point `depositETH` passes `msg.value` as `depositAmount` to `_beforeDeposit` ( [3](#0-2) ), which in turn passes it as `amount` to the broken check — confirming the full call path is reachable by any unprivileged caller.

## Impact Explanation
`depositLimitByAsset[ETH_TOKEN]` is the protocol's primary risk-management cap on ETH exposure. Bypassing it allows unbounded rsETH minting beyond the intended ceiling. If excess ETH cannot be fully restaked into EigenLayer strategies, it sits idle in the deposit pool and does not earn restaking rewards, degrading yield for all rsETH holders. The deposit cap is a protocol invariant; its violation breaks the accounting guarantee that `getTotalAssetDeposits(ETH) ≤ depositLimit` without directly stealing funds.

**Impact: Low — Contract fails to deliver promised returns.**

## Likelihood Explanation
The entry point is the public, payable `depositETH` function — no special role or privilege is required. Any depositor who observes that `totalAssetDeposits ≤ depositLimit` can send an arbitrarily large ETH deposit in a single call. The condition is trivially satisfiable whenever the protocol is not already over-limit, and the exploit is repeatable across multiple transactions.

## Recommendation
Add `amount` to the ETH branch to match the ERC-20 logic:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

## Proof of Concept
Assume `depositLimitByAsset[ETH_TOKEN] = 1000 ETH` and `totalAssetDeposits = 999 ETH`.

1. Attacker calls `depositETH{value: 500 ETH}(0, "")`.
2. `_beforeDeposit` calls `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 500e18)`.
3. ETH branch evaluates `999e18 > 1000e18` → `false`. Guard does not revert.
4. `_mintRsETH` mints rsETH for 500 ETH, pushing total ETH deposits to 1499 ETH — 49.9% above the configured limit.
5. The attacker (or any depositor) can repeat this indefinitely as long as `totalAssetDeposits ≤ depositLimit` at the start of each transaction.

**Foundry invariant test plan:** Deploy `LRTDepositPool` with `depositLimitByAsset[ETH_TOKEN] = X`. Fuzz `depositETH` calls with arbitrary `msg.value`. Assert invariant: `getTotalAssetDeposits(ETH_TOKEN) ≤ depositLimitByAsset[ETH_TOKEN]` after every call. The invariant will break immediately on the first deposit that would push total past the limit.

### Citations

**File:** contracts/LRTDepositPool.sol (L87-87)
```text
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);
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
