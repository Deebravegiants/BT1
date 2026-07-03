The code is confirmed exactly as described. Line 679 uses `totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)` for ETH, omitting `+ amount`, while line 681 correctly uses `totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)` for ERC20 tokens. [1](#0-0) [2](#0-1) [3](#0-2) 

---

Audit Report

## Title
ETH Deposit Limit Not Enforced Due to Missing `amount` in Boundary Check - (File: contracts/LRTDepositPool.sol)

## Summary
`_checkIfDepositAmountExceedesCurrentLimit` omits the incoming `amount` from the ETH branch limit check (line 679), evaluating only whether the current total already exceeds the cap rather than whether the new deposit would breach it. This allows any depositor to push ETH TVL above the admin-configured `depositLimitByAsset` cap, while the equivalent ERC20 check on line 681 correctly includes `amount`.

## Finding Description
In `_checkIfDepositAmountExceedesCurrentLimit` (L676–682), the ETH branch at line 679 returns:

```solidity
return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
```

The ERC20 branch at line 681 returns:

```solidity
return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
```

The missing `+ amount` in the ETH branch means the guard only triggers when the cap is *already* exceeded, not when the incoming deposit *would* exceed it. The reachable call path is: `depositETH()` (L76–93) → `_beforeDeposit()` (L648–663) → `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, msg.value)`. When `totalAssetDeposits` is just below the limit, the ETH check returns `false` regardless of `msg.value`, so `_beforeDeposit` does not revert and the full deposit is accepted and minted.

## Impact Explanation
The ETH deposit cap — the primary on-chain risk-management control for ETH exposure — is silently bypassed for any deposit that would cross the boundary. The protocol mints rsETH for the full over-limit amount. No funds are stolen, but the protocol fails to enforce its own stated deposit limit. This matches **Low — Contract fails to deliver promised returns, but doesn't lose value**.

## Likelihood Explanation
`depositETH` is a public, permissionless function requiring no special role. Any depositor who observes the current ETH TVL approaching the limit can send a single transaction exceeding the remaining capacity. The condition is structurally wrong for every ETH deposit that crosses the boundary, so it is triggered deterministically without front-running, governance access, or privileged keys.

## Recommendation
Add `amount` to the ETH branch to match the ERC20 logic:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

## Proof of Concept
1. Admin sets `depositLimitByAsset[ETH_TOKEN] = 1000 ether`.
2. `getTotalAssetDeposits(ETH_TOKEN)` returns `999 ether`.
3. Attacker calls `depositETH{value: 100 ether}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 100 ether)` evaluates `999 ether > 1000 ether` → `false` → no revert.
5. 100 ETH is accepted; rsETH is minted; total ETH is now 1099 ETH, 99 ETH above the cap.
6. The same call with an ERC20 asset evaluates `999 + 100 > 1000` → `true` → reverts with `MaximumDepositLimitReached`.

**Foundry test plan:** Deploy `LRTDepositPool` with a mock `LRTConfig` returning `depositLimitByAsset = 1000 ether`. Seed the pool so `getTotalAssetDeposits(ETH_TOKEN) = 999 ether`. Call `depositETH{value: 100 ether}` from an unprivileged address and assert it does not revert and that the post-deposit total exceeds 1000 ether. Then run the same scenario with an ERC20 asset and assert it reverts.

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

**File:** contracts/LRTDepositPool.sol (L648-663)
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
