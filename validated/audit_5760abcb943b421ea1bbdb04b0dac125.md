Audit Report

## Title
Stale Stored `rsETHPrice` Used in `getRsETHAmountToMint()` Allows Depositors to Capture Unclaimed Yield from Existing Holders - (File: contracts/LRTDepositPool.sol)

## Summary
`LRTDepositPool.getRsETHAmountToMint()` divides a live Chainlink asset price by `lrtOracle.rsETHPrice()`, a cached state variable that is only updated by explicit calls to `updateRSETHPrice()`. Between updates, as yield accrues (stETH rebases, EigenLayer rewards), the true rsETH/ETH rate rises above the stored value. Any depositor who calls `depositETH()` or `depositAsset()` while the price is stale receives more rsETH than they are entitled to, permanently diluting existing holders and extracting their unclaimed yield.

## Finding Description
`LRTOracle` stores the rsETH/ETH exchange rate in the state variable `rsETHPrice` (L28). This value is only written by `_updateRsETHPrice()`, which is invoked either by the permissionless `updateRSETHPrice()` (L87–89) or the manager-gated `updateRSETHPriceAsManager()` (L94–96). No deposit path triggers a price refresh.

`getRsETHAmountToMint()` (L506–521) computes:
```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```
`lrtOracle.getAssetPrice(asset)` (L156–158) delegates to a live `IPriceFetcher`, returning the current Chainlink price. `lrtOracle.rsETHPrice()` returns the last written snapshot. The two inputs are therefore from different points in time.

`_beforeDeposit()` (L648–670) calls `getRsETHAmountToMint()` directly with no price refresh, and both `depositETH()` (L76–93) and `depositAsset()` (L99–118) call `_beforeDeposit()` without any guard.

`_updateRsETHPrice()` (L214–316) computes the true price from `_getTotalEthInProtocol()` (L331–349), which sums `currentBalance × liveChainlinkPrice` for every supported asset. After yield accrues (stETH rebase increases balances, EigenLayer rewards increase ETH held), `_getTotalEthInProtocol()` returns a higher value, so the true rsETH price is higher than the stored snapshot. A depositor who acts before the keeper calls `updateRSETHPrice()` uses the stale (lower) denominator and receives excess rsETH.

Existing checks are insufficient:
- `minRSETHAmountExpected` protects the depositor from receiving *too little*, not existing holders from dilution.
- `pricePercentageLimit` (L252–266) limits per-update price jumps but does not prevent the stale-price window.
- `updateRSETHPrice()` is permissionless but the attacker simply does not call it.

## Impact Explanation
When `rsETHPrice_stored < rsETHPrice_true`, a depositor of `X` ETH receives `X / rsETHPrice_stored > X / rsETHPrice_true` rsETH. The excess rsETH represents a claim on TVL not contributed by the depositor — it is yield that belongs to existing holders. After `updateRSETHPrice()` is called, the new price is computed over the enlarged supply, permanently diluting prior holders. This is **theft of unclaimed yield**, a High-severity impact under the allowed scope.

## Likelihood Explanation
`updateRSETHPrice()` is called by an off-chain keeper on a periodic schedule. The window between updates is a normal operating condition, not an edge case. Any unprivileged external user can call `depositETH()` or `depositAsset()` at any time with no special role. The attacker only needs to deposit after yield has accrued but before the keeper refreshes the price — a condition that recurs every update cycle. No front-running, flash loans, or privileged access are required.

## Recommendation
Atomically refresh `rsETHPrice` inside `_beforeDeposit()` (or `getRsETHAmountToMint()`) before computing the mint amount, so the denominator always reflects the current on-chain TVL:
```solidity
lrtOracle.updateRSETHPrice(); // refresh before minting
rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);
```
Alternatively, expose a pure view function in `LRTOracle` that computes the current rsETH price on-the-fly from `_getTotalEthInProtocol()` and `rsethSupply` without writing state, and use that in `getRsETHAmountToMint()` instead of the stored `rsETHPrice`.

## Proof of Concept
1. Protocol state: `rsethSupply = 1000 rsETH`, `rsETHPrice = 1.00 ETH` (stored), true TVL = 1050 ETH (50 ETH yield has accrued via stETH rebase since last update; true price = 1.05 ETH). `updateRSETHPrice()` has not been called.
2. Attacker calls `depositETH{value: 105 ETH}(0, "")`.
3. `getRsETHAmountToMint` computes: `105e18 * 1e18 / 1.00e18 = 105 rsETH` (stale denominator). Correct amount at true price: `105 / 1.05 = 100 rsETH`. Attacker receives **5 extra rsETH**.
4. Keeper calls `updateRSETHPrice()`. New supply = 1105 rsETH, TVL = 1155 ETH. New price = `1155 / 1105 ≈ 1.0453 ETH`.
5. Attacker's 105 rsETH is worth `105 × 1.0453 ≈ 109.76 ETH` — a profit of ~4.76 ETH extracted from the 50 ETH yield that belonged to the original 1000 rsETH holders.

**Foundry fork test plan**: Fork mainnet, set `rsETHPrice` to a value 5% below the value that `_getTotalEthInProtocol()` would compute, call `depositETH` as an unprivileged address, assert that `rsETH.balanceOf(attacker)` exceeds `depositAmount.divWad(truePrice)`, then call `updateRSETHPrice()` and assert that the attacker's rsETH is worth more ETH than deposited, at the expense of pre-existing holders' share of TVL.