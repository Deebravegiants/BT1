Audit Report

## Title
Stale Cached `rsETHPrice` Enables Over-Minting on Deposit and Over-Redemption on Instant Withdrawal - (File: `contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`, `contracts/LRTWithdrawalManager.sol`)

## Summary

`LRTOracle.rsETHPrice` is a persistent state variable updated only when `_updateRsETHPrice()` is explicitly called. Both `LRTDepositPool.getRsETHAmountToMint()` and `LRTWithdrawalManager.getExpectedAssetAmount()` divide by this stale cached value while reading live asset prices via `getAssetPrice()`. The resulting price mismatch allows an unprivileged attacker to receive more rsETH on deposit (when LST prices have risen) or more underlying assets on instant withdrawal (when LST prices have fallen) than their fair share, directly stealing value from other depositors.

## Finding Description

**Root cause:** `rsETHPrice` is a cached state variable in `LRTOracle`:

```solidity
// LRTOracle.sol:28
uint256 public override rsETHPrice;
```

It is only updated inside `_updateRsETHPrice()`, called via the public `updateRSETHPrice()` or manager-gated `updateRSETHPriceAsManager()`. No on-chain mechanism forces a refresh before any user-facing operation.

**Deposit path** (`LRTDepositPool.sol:520`):
```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```
`getAssetPrice(asset)` fetches a live Chainlink price; `rsETHPrice()` returns the stale cached value. When LST prices rise between two `updateRSETHPrice()` calls, the true rsETHPrice is higher than stored. A depositor acting in this window receives more rsETH than their deposit is worth, diluting all existing holders.

**Instant-withdrawal path** (`LRTWithdrawalManager.sol:593`):
```solidity
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```
When LST prices fall and `rsETHPrice` is stale-high, an attacker calling `instantWithdrawal` before `updateRSETHPrice()` receives more underlying assets than their rsETH is truly worth. Critically, unlike the queued-withdrawal path which applies a `min(expectedAmount, currentReturn)` guard in `_calculatePayoutAmount` (`LRTWithdrawalManager.sol:833–834`), `instantWithdrawal` has **no such guard** — it transfers the full stale-inflated amount immediately.

**Why existing checks are insufficient:**

- The `pricePercentageLimit` auto-pause in `_updateRsETHPrice()` (`LRTOracle.sol:270–281`) only triggers when `updateRSETHPrice()` is called. The attacker exploits the window *before* that call.
- The `CantInstantWithdrawMoreThanAvailable` check (`LRTWithdrawalManager.sol:231–233`) limits total withdrawal size but does not prevent the price-inflated per-unit calculation.
- `isInstantWithdrawalEnabled[asset]` gates the instant withdrawal path but is a normal operational toggle, not a security control against this attack.

## Impact Explanation

**Critical — direct theft of user funds.**

- **Instant-withdrawal:** Attacker burns rsETH and receives more underlying LST than the rsETH is worth at the true current price. The excess is drawn directly from the pool's assets, reducing the redemption value for all remaining depositors.
- **Deposit:** Attacker mints more rsETH than their deposit warrants. After `updateRSETHPrice()` is called, the attacker's rsETH is worth more than deposited; the dilution is borne by all existing holders.

Both paths result in direct, quantifiable, irreversible loss to other protocol participants.

## Likelihood Explanation

**Medium.**

- `updateRSETHPrice()` is public and called by off-chain bots, but there is no on-chain freshness enforcement. Every block between two update calls is a valid attack window.
- LST prices (stETH/ETH, ETHx/ETH) fluctuate continuously via Chainlink. Even 0.1–0.5% deviations over a multi-block window are sufficient for a profitable attack at scale.
- The deposit-side dilution path is always open when the protocol is unpaused and requires no special role.
- The instant-withdrawal path requires `isInstantWithdrawalEnabled[asset] == true`, which is an operational setting, not a permanent barrier.
- The attacker needs no special role — any rsETH holder or LST depositor can execute this.

## Recommendation

1. **Atomically refresh `rsETHPrice` before every deposit and instant withdrawal.** Call `_updateRsETHPrice()` (or an equivalent live computation) inside `_beforeDeposit` and at the start of `instantWithdrawal` rather than reading the cached state variable.
2. **Alternatively, compute the share price on-the-fly** using `_getTotalEthInProtocol() / rsethSupply` at the point of use, eliminating the cached value entirely for user-facing operations.
3. **Apply the same `min(expectedAmount, currentReturn)` guard** used in `_calculatePayoutAmount` to `instantWithdrawal`, so that even with a stale price, the user cannot receive more than the current fair value.
4. **Add a staleness guard** on `rsETHPrice` (e.g., a `lastUpdatedTimestamp` that must be within N blocks) and revert deposits/withdrawals if the price is stale.

## Proof of Concept

**Instant-withdrawal theft (requires `isInstantWithdrawalEnabled[stETH] == true`):**

1. Block B: stETH/ETH Chainlink = 1.01. `updateRSETHPrice()` called; `rsETHPrice` = 1.01. Pool holds 10,000 stETH, 9,901 rsETH outstanding.
2. Block B+10: stETH/ETH Chainlink drops to 0.99 (depeg). True rsETHPrice = `10,000 × 0.99 / 9,901` ≈ 0.99. Stored `rsETHPrice` = 1.01 (stale — `updateRSETHPrice()` not yet called).
3. Attacker (holds 1,000 rsETH) calls `instantWithdrawal(stETH, 1000)`:
   - `getExpectedAssetAmount(stETH, 1000)` = `1000 × 1.01 / 0.99` ≈ **1020.2 stETH**
   - Fair value: `1000 × 0.99 / 0.99` = **1000 stETH**
   - Attacker receives **~20.2 stETH excess**, stolen from remaining depositors.
4. `updateRSETHPrice()` subsequently called; remaining depositors' rsETH is now backed by fewer assets.

**Deposit-side dilution (always available when unpaused):**

1. Block B: stETH/ETH = 0.99. `rsETHPrice` = 0.99 (updated).
2. Block B+5: stETH/ETH rises to 1.01 (live Chainlink). True rsETHPrice ≈ 1.01. Stored `rsETHPrice` = 0.99 (stale).
3. Attacker deposits 1,000 stETH:
   - `getRsETHAmountToMint(stETH, 1000)` = `1000 × 1.01 / 0.99` ≈ **1020.2 rsETH**
   - Fair amount: `1000 × 1.01 / 1.01` = **1000 rsETH**
   - Attacker receives **~20.2 rsETH excess** at existing holders' expense.
4. `updateRSETHPrice()` called; attacker's rsETH is now worth more than deposited.

**Foundry fork test plan:** Fork mainnet at a block where `rsETHPrice` was last updated N blocks prior. Warp/roll forward to simulate Chainlink price movement without an intervening `updateRSETHPrice()` call. Call `depositAsset` or `instantWithdrawal` and assert that the received rsETH / underlying exceeds the fair-value amount computed from `_getTotalEthInProtocol() / rsethSupply` at the same block.