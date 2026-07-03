Audit Report

## Title
ETH Deposit Limit Bypass Due to Asymmetric Comparison in `_checkIfDepositAmountExceedesCurrentLimit` - (File: contracts/LRTDepositPool.sol)

## Summary
`_checkIfDepositAmountExceedesCurrentLimit` uses a strict greater-than check (`>`) for ETH without including the incoming `amount`, while ERC20 assets correctly use `totalAssetDeposits + amount > limit`. When `getTotalAssetDeposits(ETH_TOKEN)` equals the configured cap exactly, the ETH branch returns `false`, `_beforeDeposit` does not revert, and `depositETH` mints rsETH and accepts the ETH — pushing the running total above the cap. Any unprivileged depositor can trigger this with a single `depositETH` call.

## Finding Description
In `contracts/LRTDepositPool.sol` at lines 676–682, the function branches on `asset == LRTConstants.ETH_TOKEN`:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // amount ignored
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

The `amount` parameter is never used in the ETH branch. The check only asks whether the total is **already** strictly above the limit. When `totalAssetDeposits == depositLimitByAsset(ETH_TOKEN)`, the expression `totalAssetDeposits > limit` evaluates to `false`, so `_checkIfDepositAmountExceedesCurrentLimit` returns `false`. Back in `_beforeDeposit` (lines 661–663), the `MaximumDepositLimitReached` revert is skipped, and execution continues to `_mintRsETH`. The `depositETH` entry point (lines 76–93) passes `msg.value` as `depositAmount`, so any nonzero ETH deposit at this boundary state bypasses the cap entirely.

The ERC20 path is unaffected because `amount` is included in the comparison on line 681.

## Impact Explanation
**Low — Contract fails to deliver promised returns, but doesn't lose value.**

The ETH deposit cap (`depositLimitByAsset`) is the protocol's primary supply-control invariant for ETH. Bypassing it causes `getTotalAssetDeposits(ETH_TOKEN)` to exceed the configured limit, violating the invariant `totalDeposits ≤ cap` after every deposit. This results in more rsETH being minted than the cap intends, diluting existing rsETH holders by a small amount proportional to the excess deposit. No funds are stolen; the depositor provides real ETH. The impact is a broken protocol guarantee, matching the allowed Low impact class.

## Likelihood Explanation
The precondition — `getTotalAssetDeposits(ETH_TOKEN) == depositLimitByAsset(ETH_TOKEN)` — is transient but operationally reachable. A common administrative pattern is to set the limit equal to the current total to halt further inflows; at that moment any depositor can immediately call `depositETH` with any `msg.value > 0` to exceed the cap. `getTotalAssetDeposits` aggregates across the deposit pool, NDCs, EigenLayer strategies, the converter, and the unstaking vault, so the exact equality can also arise naturally as deposits accumulate. No privileged access is required; the exploit is a single public call.

## Recommendation
Remove the ETH-specific branch and apply the prospective check uniformly:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

This makes ETH and ERC20 paths consistent and ensures the cap is never exceeded regardless of the current total.

## Proof of Concept
1. Admin calls `setDepositLimitByAsset(ETH_TOKEN, 100 ether)`.
2. Through normal deposits, `getTotalAssetDeposits(ETH_TOKEN)` reaches exactly `100 ether`.
3. Alice calls `depositETH(0, "ref")` with `msg.value = 1 ether`.
4. `_beforeDeposit(ETH_TOKEN, 1 ether, 0)` invokes `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 1 ether)`.
5. Inside: `totalAssetDeposits = 100 ether`, `limit = 100 ether`; ETH branch evaluates `100 ether > 100 ether` → `false`.
6. `_beforeDeposit` does not revert; `_mintRsETH` mints rsETH for Alice.
7. `getTotalAssetDeposits(ETH_TOKEN)` is now `101 ether`, exceeding the cap by `1 ether`.

**Foundry invariant test sketch:**
```solidity
function invariant_ethDepositCapNeverExceeded() public {
    uint256 total = depositPool.getTotalAssetDeposits(ETH_TOKEN);
    uint256 cap   = lrtConfig.depositLimitByAsset(ETH_TOKEN);
    assertLe(total, cap, "ETH deposit cap exceeded");
}
```
Running this invariant with a fuzzer that calls `depositETH` with varying `msg.value` values after setting the cap to the current total will reproduce the violation on the first iteration where `totalAssetDeposits == cap`.