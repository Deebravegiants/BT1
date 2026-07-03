Audit Report

## Title
stETH Transfer Shortfall Causes rsETH Over-Minting in `depositAsset()` - (File: contracts/LRTDepositPool.sol)

## Summary
`LRTDepositPool.depositAsset()` computes `rsethAmountToMint` from the caller-supplied `depositAmount` before executing `safeTransferFrom`. Because stETH is a rebasing, share-based token that delivers 1–2 wei less than the nominal transfer amount due to internal share rounding, the pool mints rsETH against a larger nominal deposit than the actual balance received. This creates a persistent, accumulating undercollateralization that dilutes existing rsETH holders.

## Finding Description
In `contracts/LRTDepositPool.sol` lines 110–117, `_beforeDeposit` is called first to compute `rsethAmountToMint` from the user-supplied `depositAmount`, and only afterward does the actual token transfer occur:

```solidity
// LRTDepositPool.sol L110-117
uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);
IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
_mintRsETH(rsethAmountToMint);
```

`_beforeDeposit` delegates to `getRsETHAmountToMint(asset, depositAmount)` at line 665, which computes `(depositAmount * assetPrice) / rsETHPrice` — using the full nominal `depositAmount`, not the actual received balance.

stETH is a first-class supported asset: `LRTConfig.initialize()` at line 56 explicitly registers it via `_addNewSupportedAsset(stETH, 100_000 ether)`, and `LRTDepositPool` imports `ILido` and exposes `stakeEthForStETH`. stETH internally tracks balances as shares; when `transferFrom` is called for a specific token amount, the contract converts to shares (rounding down) and back, delivering `depositAmount − 1` or `depositAmount − 2` wei to the recipient. No existing check in `_beforeDeposit` or `depositAsset` measures the actual balance delta after the transfer. The minted rsETH is therefore calculated from a nominal amount that is 1–2 wei larger than what the pool actually holds.

## Impact Explanation
Every stETH deposit mints 1–2 wei worth of rsETH in excess of the actual assets received. The shortfall accumulates across all stETH deposits, causing the protocol to be persistently undercollateralized. Existing rsETH holders bear the dilution: the real asset backing per rsETH unit is fractionally lower than it should be after each stETH deposit. This matches the **Low** severity impact class: **"Contract fails to deliver promised returns"** — the protocol promises rsETH is fully backed by deposited assets, but each stETH deposit breaks that invariant by 1–2 wei.

## Likelihood Explanation
stETH is a core, explicitly initialized supported asset. Any unprivileged external user calling `depositAsset(stETH, ...)` triggers the shortfall. No special conditions, attacker coordination, or privileged access are required. The condition is deterministic and repeatable on every stETH deposit. **Likelihood: Medium.**

## Recommendation
Measure the actual balance delta after the transfer and use that for minting:

```solidity
function depositAsset(
    address asset,
    uint256 depositAmount,
    uint256 minRSETHAmountExpected,
    string calldata referralId
) external nonReentrant whenNotPaused onlySupportedERC20Token(asset) {
    uint256 balanceBefore = IERC20(asset).balanceOf(address(this));
    IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
    uint256 actualReceived = IERC20(asset).balanceOf(address(this)) - balanceBefore;

    uint256 rsethAmountToMint = _beforeDeposit(asset, actualReceived, minRSETHAmountExpected);
    _mintRsETH(rsethAmountToMint);
    emit AssetDeposit(msg.sender, asset, actualReceived, rsethAmountToMint, referralId);
}
```

This pattern also future-proofs the contract against any other fee-on-transfer or rebasing tokens that may be added as supported assets.

## Proof of Concept
1. Alice calls `LRTDepositPool.depositAsset(stETH, 1e18, 0, "")`.
2. `_beforeDeposit` computes `rsethAmountToMint` from `1e18` stETH at the current oracle price (e.g., `~0.9997e18` rsETH).
3. `safeTransferFrom` executes; due to stETH share rounding, the pool receives `1e18 − 1` wei of stETH.
4. `_mintRsETH(~0.9997e18)` mints rsETH calculated from `1e18`, not `1e18 − 1`.
5. The pool is now short 1 wei of stETH relative to the rsETH it has issued.
6. Repeated across thousands of deposits, the shortfall grows, fractionally diluting all rsETH holders.

**Foundry fork test plan:** Fork mainnet, deploy/use the live `LRTDepositPool`. Record `IERC20(stETH).balanceOf(pool)` before and after `depositAsset(stETH, 1e18, 0, "")`. Assert that `balanceAfter - balanceBefore < 1e18` while `rsethAmountToMint` was computed from `1e18`. The invariant `totalAssetValue >= totalRsETHSupply * rsETHPrice` will be violated by 1–2 wei after the call.