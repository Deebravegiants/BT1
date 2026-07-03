Audit Report

## Title
Stale `rsETHPrice` Enables Yield Theft via Deposit at Outdated Exchange Rate - (File: contracts/LRTDepositPool.sol)

## Summary
`LRTOracle.updateRSETHPrice()` is a public, permissionless function that updates the stored `rsETHPrice` state variable. Between updates, `rsETHPrice` becomes stale while underlying LST assets accrue yield and their Chainlink prices drift upward. Because `LRTDepositPool.getRsETHAmountToMint()` divides by the stale stored `rsETHPrice` while using a live Chainlink numerator, an attacker can deposit at the artificially low denominator to receive more rsETH than fair value, then trigger or wait for a price update to realize the gain at the expense of existing holders.

## Finding Description
`LRTOracle.updateRSETHPrice()` is callable by any address when the contract is not paused:

```solidity
// LRTOracle.sol L87-89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

The stored `rsETHPrice` is only written inside `_updateRsETHPrice()` at line 313. Between calls, it remains fixed while the real TVL grows as stETH, ETHx, and other LSTs accrue staking rewards.

When a user deposits, `getRsETHAmountToMint()` computes the mint amount as:

```solidity
// LRTDepositPool.sol L520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`lrtOracle.getAssetPrice(asset)` reads a **live** Chainlink price (via `IPriceFetcher`), while `lrtOracle.rsETHPrice()` returns the **stale** cached value. When `rsETHPrice` is lower than the true current rate, the denominator is too small and the depositor receives more rsETH than their deposit is worth at the true exchange rate.

The `pricePercentageLimit` guard inside `_updateRsETHPrice()` (lines 252–266) compares `newRsETHPrice` against `highestRsethPrice`. Since both `rsETHPrice` and `highestRsethPrice` are updated together and become stale together, normal daily yield accrual (e.g., ~0.01–0.05% per day) will typically fall within the configured limit, allowing an unprivileged caller to successfully invoke `updateRSETHPrice()`. Even if the limit is exceeded, the attacker can still deposit at the stale price and wait for the manager to call `updateRSETHPriceAsManager()`.

No freshness check, staleness window, or atomic price-update-before-mint exists in `_beforeDeposit()` (lines 648–670) or `depositETH()`/`depositAsset()`.

## Impact Explanation
**High — Theft of unclaimed yield.**

Each time the attacker executes this pattern, they extract a portion of the yield that accrued since the last `rsETHPrice` update. The over-minted rsETH represents a claim on more ETH than the attacker deposited; the shortfall is borne by all existing rsETH holders whose proportional share of the TVL is diluted. The attack is repeatable every update cycle, bounded only by the yield accumulated per interval.

## Likelihood Explanation
**Medium.**

The attacker requires no special role, no leaked key, and no oracle compromise. All required information (current Chainlink asset prices vs. stored `rsETHPrice`) is fully on-chain and observable by anyone. The steps are:
1. Read `lrtOracle.rsETHPrice()` and compare against the live TVL implied by `_getTotalEthInProtocol()` logic (reproducible off-chain or via a view call).
2. Deposit at the stale price.
3. Call `updateRSETHPrice()` (or wait for the protocol keeper to do so).

The attack is self-contained, requires no victim interaction, and is repeatable on every update cycle.

## Recommendation
1. **Atomic price refresh on deposit:** At the start of `_beforeDeposit()`, call `ILRTOracle(lrtOracleAddress).updateRSETHPrice()` (or an internal equivalent) before computing `rsethAmountToMint`. This ensures the mint price always reflects the current TVL.
2. **Compute mint amount from live TVL directly:** Replace the stored `rsETHPrice` denominator in `getRsETHAmountToMint()` with an on-the-fly calculation using `_getTotalEthInProtocol()` and `rsETH.totalSupply()`, bypassing the stale cache entirely.
3. **Staleness bound:** Enforce a maximum age for `rsETHPrice` (e.g., revert if `block.timestamp - lastPriceUpdateTimestamp > MAX_STALENESS`) inside `getRsETHAmountToMint()`.

## Proof of Concept
**Setup:** `rsETHPrice = 1.01e18` (last updated 24 hours ago). Yield has accrued; true rsETH price is now `1.012e18`.

**Attack steps:**

1. Attacker calls `LRTDepositPool.depositETH{value: 100 ether}(0, "")`.
   - `getAssetPrice(ETH_TOKEN)` → `1e18` (live Chainlink).
   - `rsETHPrice()` → `1.01e18` (stale stored value).
   - `rsethAmountToMint = 100e18 * 1e18 / 1.01e18 ≈ 99.0099 rsETH`.
   - Fair amount at true price: `100e18 / 1.012e18 ≈ 98.8142 rsETH`.
   - Over-minted: `≈ 0.1957 rsETH`.

2. Attacker calls `LRTOracle.updateRSETHPrice()`.
   - `rsETHPrice` updates to approximately `1.012e18` (slightly reduced by the dilution from step 1, but still higher than `1.01e18`).

3. Attacker redeems/sells `≈ 99.0099 rsETH` at the new price.
   - Value: `99.0099 × 1.012e18 / 1e18 ≈ 100.198 ETH`.
   - Profit: `≈ 0.198 ETH` extracted from existing holders.

**Foundry fork test plan:**
```solidity
function testStaleRsETHPriceYieldTheft() public {
    // 1. Fork mainnet, advance time by 1 day without calling updateRSETHPrice
    // 2. Record rsETHPrice (stale) and compute true price via _getTotalEthInProtocol equivalent
    // 3. Deposit 100 ETH as attacker, record rsETH minted
    // 4. Call updateRSETHPrice()
    // 5. Assert attacker rsETH * newRsETHPrice > 100 ETH (profit at existing holders' expense)
    // 6. Assert existing holder rsETH * newRsETHPrice < pre-attack equivalent (dilution)
}
```