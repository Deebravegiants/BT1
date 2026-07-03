The code at lines 676-682 confirms the vulnerability exactly as described. The ETH branch omits `amount` from the comparison while the ERC20 branch correctly includes it. [1](#0-0) [2](#0-1) 

---

Audit Report

## Title
ETH Deposit Limit Bypass via Missing Amount in `_checkIfDepositAmountExceedesCurrentLimit` - (File: contracts/LRTDepositPool.sol)

## Summary
`_checkIfDepositAmountExceedesCurrentLimit` omits the incoming `amount` from the ETH branch comparison (`totalAssetDeposits > limit`) while correctly including it for ERC20 assets (`totalAssetDeposits + amount > limit`). Any unprivileged caller can invoke `depositETH` with an arbitrarily large `msg.value` and bypass the configured `depositLimitByAsset[ETH_TOKEN]` cap, minting rsETH beyond the protocol's intended ceiling.

## Finding Description
The guard function at `contracts/LRTDepositPool.sol` L676–682 contains an asymmetric check:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)); // amount ignored
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // correct
}
```

`_beforeDeposit` (L661–663) calls this function and reverts with `MaximumDepositLimitReached` only when it returns `true`. For ETH, the function returns `true` only if the existing total already exceeds the limit — the prospective deposit `amount` is never factored in. As long as `totalAssetDeposits <= depositLimit` at call time, the check always returns `false` regardless of `msg.value`, and `depositETH` (L76–93) proceeds to mint rsETH for the full deposit.

## Impact Explanation
The `depositLimitByAsset` cap is the protocol's primary mechanism for bounding ETH intake. Bypassing it allows rsETH to be minted against ETH deposits that exceed the intended ceiling. This concretely maps to **Low — contract fails to deliver promised returns**: the deposit cap invariant is broken and the protocol accepts more ETH than intended. It also creates a realistic path to **Medium — temporary freezing of funds**: excess ETH accumulates in the deposit pool or NDCs with no downstream EigenLayer strategy capacity to absorb it, leaving those funds unable to be forwarded and effectively frozen until manual intervention.

## Likelihood Explanation
The exploit path is fully permissionless. Any external user can call `depositETH{value: X}(0, "")` where `X` exceeds the remaining cap. No special role, privileged access, front-running, or external dependency is required. The condition is reachable whenever the ETH deposit limit is set to a finite value and the pool is unpaused — both normal operating conditions.

## Recommendation
Remove the ETH-specific branch and apply the same `totalAssetDeposits + amount` logic uniformly:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

## Proof of Concept
1. Admin sets `depositLimitByAsset[ETH_TOKEN] = 1000 ether`.
2. Prior deposits bring `getTotalAssetDeposits(ETH_TOKEN)` to exactly `1000 ether`.
3. Attacker calls `depositETH{value: 500 ether}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 500 ether)` evaluates `1000 ether > 1000 ether` → `false` → guard passes.
5. `_mintRsETH` mints rsETH for 500 ETH; total ETH deposits become `1500 ether`, 50% above the cap.
6. Contrast: `depositAsset(stETH, 500 ether, ...)` at the same state evaluates `1000 + 500 > 1000` → `true` → correctly reverts with `MaximumDepositLimitReached`.

**Foundry test plan:** Deploy `LRTDepositPool` with a mock `LRTConfig` returning `depositLimitByAsset = 1000 ether`. Seed `getTotalAssetDeposits(ETH_TOKEN)` to `1000 ether`. Call `depositETH{value: 500 ether}`. Assert the call succeeds (no revert) and `getTotalAssetDeposits(ETH_TOKEN)` returns `1500 ether`, confirming the cap was bypassed.

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
