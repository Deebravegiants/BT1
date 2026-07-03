Audit Report

## Title
Stale `rsETHPrice` Denominator in `getRsETHAmountToMint` Enables Theft of Unclaimed Yield — (`contracts/LRTDepositPool.sol`, `contracts/LRTOracle.sol`)

## Summary

`getRsETHAmountToMint` divides by the cached state variable `rsETHPrice`, which is only updated on explicit calls to `updateRSETHPrice()`. Because stETH is a rebasing token, the protocol's total ETH backing grows automatically between price updates. Any depositor who deposits during this window receives more rsETH than their fair share, permanently capturing yield that belongs to existing holders.

## Finding Description

`getRsETHAmountToMint` computes the mint amount as:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [1](#0-0) 

The numerator uses `getAssetPrice(asset)`, which reads live from Chainlink and returns the current stETH/ETH exchange rate. The denominator uses `lrtOracle.rsETHPrice()`, which reads the cached state variable:

```solidity
uint256 public override rsETHPrice;
``` [2](#0-1) 

This value is only updated when `updateRSETHPrice()` / `_updateRsETHPrice()` is explicitly called: [3](#0-2) 

`_updateRsETHPrice()` computes the new price from `_getTotalEthInProtocol()`, which sums `totalAssetAmt * assetER` across all supported assets: [4](#0-3) 

When stETH rebases, `IERC20(stETH).balanceOf(...)` increases across the deposit pool, NDCs, and unstaking vault — so `getTotalAssetDeposits(stETH)` grows — but `rsETHPrice` does **not** update automatically. The stored price is therefore lower than the true backing ratio.

`_beforeDeposit` performs no freshness check on `rsETHPrice` and calls `getRsETHAmountToMint` directly: [5](#0-4) 

`depositAsset` and `depositETH` both flow through `_beforeDeposit` without first calling `updateRSETHPrice()`: [6](#0-5) 

`minRSETHAmountExpected` is caller-controlled and provides no protection against over-minting — an attacker simply sets it to the inflated amount they expect to receive.

**Arithmetic proof of theft:**
- Let `P = rsETHPrice` (stale), `P_true = (E + δ) / S` (true backing after rebase of `δ`)
- Attacker deposits `A` stETH (worth `A * stETHPrice` ETH)
- Minted: `staleRsETH = A * stETHPrice / P`
- Fair amount: `fairRsETH = A * stETHPrice / P_true`
- Since `P < P_true`, `staleRsETH > fairRsETH`
- After `updateRSETHPrice()` is called, `previousTVL = (S + staleRsETH) * P = E + A * stETHPrice`, so `rewardAmount = totalETHInProtocol - previousTVL = δ` — the rebase yield is still attributed to the period, but the attacker's excess rsETH already represents a claim on part of `δ` at the new price `P_true`
- Attacker profit = `(staleRsETH - fairRsETH) * P_true > 0`, funded entirely by diluting existing holders' share of `δ`

## Impact Explanation

This is **Theft of unclaimed yield (High)**. Existing rsETH holders' accrued stETH rebase yield is permanently redistributed to the attacker. The protocol does not become insolvent — total backing still covers total supply — but the yield is irreversibly diluted from existing holders. The magnitude per attack is bounded by the yield accrued since the last price update (stETH APY ≈ 3–4% / 365 ≈ 0.01% per day of TVL), but it is repeatable every update cycle and scales with deposit size.

## Likelihood Explanation

- `updateRSETHPrice()` is public but not called atomically with deposits; there is always a window between yield accrual and price update.
- stETH rebases daily at a predictable and observable on-chain time.
- No special role, flashloan, or governance action is required — any EOA can exploit this.
- The attacker sets `minRSETHAmountExpected` to the inflated amount they expect, so the slippage guard does not block them.
- The attack is repeatable every rebase cycle.

## Recommendation

Before computing `rsethAmountToMint` in `_beforeDeposit`, call `_updateRsETHPrice()` (or an internal equivalent) to ensure `rsETHPrice` reflects the current backing. Alternatively, compute the mint amount on-the-fly from `_getTotalEthInProtocol()` and `rsethSupply` rather than from the cached `rsETHPrice`, so deposits always use a fresh ratio. This eliminates the window between rebase and price update.

## Proof of Concept

```solidity
// Fork mainnet at block B (stETH has just rebased, updateRSETHPrice not yet called)
// rsETHPrice = P_stale  (< true backing P_true = (E + δ) / S)

// Step 1: Attacker deposits stETH using stale price
uint256 staleRsETH = depositPool.getRsETHAmountToMint(stETH, DEPOSIT);
// staleRsETH = DEPOSIT * stETHPrice / P_stale  >  DEPOSIT * stETHPrice / P_true

depositPool.depositAsset(stETH, DEPOSIT, staleRsETH, "");
// attacker receives staleRsETH rsETH (more than fair share)

// Step 2: Anyone calls updateRSETHPrice — price rises to P_true
lrtOracle.updateRSETHPrice();
// rsETHPrice = P_true > P_stale
// rewardAmount = δ (rebase), protocol fee taken on δ, but attacker already captured excess

// Step 3: Attacker redeems
// Each rsETH is now redeemable at P_true ETH
// attacker redeems staleRsETH * P_true > DEPOSIT * stETHPrice
// profit = (staleRsETH - fairRsETH) * P_true = yield stolen from existing holders

assert(attackerETHOut > DEPOSIT * stETHPrice / 1e18); // profitable round-trip
```

**Foundry fork test plan:**
1. Fork mainnet at a block immediately after a stETH rebase event (observable via `Lido.TokenRebased` event) before `updateRSETHPrice()` is called.
2. Record `rsETHPrice` (stale) and compute `_getTotalEthInProtocol() / rsethSupply` (true price).
3. Deposit a large stETH amount as the attacker; record rsETH received.
4. Call `lrtOracle.updateRSETHPrice()`.
5. Assert `attackerRsETH * newRsETHPrice > depositAmount * stETHPrice`, confirming profitable over-minting at the expense of pre-existing holders.

### Citations

**File:** contracts/LRTDepositPool.sol (L99-118)
```text
    function depositAsset(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedERC20Token(asset)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTDepositPool.sol (L665-669)
```text
        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L341-343)
```text
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```
