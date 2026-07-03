Audit Report

## Title
rsETH Price Inflation via ETH Donation Enables First-Depositor Theft - (`contracts/LRTOracle.sol` / `contracts/LRTDepositPool.sol`)

## Summary
`LRTDepositPool.getETHDistributionData()` uses `address(this).balance` directly as the ETH TVL component, meaning any ETH sent via the unrestricted `receive()` function immediately inflates the reported TVL. Combined with a public `updateRSETHPrice()` and a price-increase guard that is permanently disabled when `pricePercentageLimit == 0` (the default), an attacker who is the first depositor can inflate `rsETHPrice` to an arbitrarily large value, causing subsequent depositors who pass `minRSETHAmountExpected = 0` to receive 0 rsETH while their ETH is permanently absorbed into the pool.

## Finding Description

**Root cause 1 — raw balance used in TVL:**
`getETHDistributionData()` assigns `ethLyingInDepositPool = address(this).balance` at line 480 of `LRTDepositPool.sol`. This value is aggregated by `_getTotalEthInProtocol()` in `LRTOracle.sol` (lines 331–348) via `ILRTDepositPool.getTotalAssetDeposits(ETH_TOKEN)`. Any ETH sent directly to the contract via `receive()` (line 58) is immediately reflected in the TVL used for price computation.

**Root cause 2 — public price update with disabled guard:**
`updateRSETHPrice()` is callable by any address (`public`, line 87 of `LRTOracle.sol`). The price-increase guard at lines 256–257 is:
```solidity
bool isPriceIncreaseOffLimit =
    pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
```
Because `initialize()` (lines 64–68) never sets `pricePercentageLimit`, it defaults to `0`, making `isPriceIncreaseOffLimit` permanently `false`. Any price increase, no matter how large, passes the guard.

**Root cause 3 — integer division truncation:**
`getRsETHAmountToMint()` at line 520 computes:
```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```
With an inflated `rsETHPrice`, any deposit smaller than the inflated price truncates to 0.

**Root cause 4 — zero-mint deposit not rejected:**
`_beforeDeposit()` at lines 667–669 only reverts if `rsethAmountToMint < minRSETHAmountExpected`. When `minRSETHAmountExpected = 0` and `rsethAmountToMint = 0`, the condition `0 < 0` is false, so the deposit proceeds, ETH is retained, and 0 rsETH is minted.

**Exploit path:**
1. At launch (rsETH supply = 0), attacker calls `updateRSETHPrice()` → `rsETHPrice = 1e18`.
2. Attacker calls `depositETH{value: 1}(0, "")` → receives 1 wei rsETH.
3. Attacker sends X ETH directly to `LRTDepositPool` via `receive()`.
4. Attacker calls `updateRSETHPrice()` → `rsETHPrice = X * 1e18 / 1 = X * 1e18`.
5. Victim calls `depositETH{value: Y}(0, "")` where Y < X → `rsethAmountToMint = Y * 1e18 / (X * 1e18) = 0` → 0 rsETH minted, Y ETH absorbed.
6. Attacker redeems 1 wei rsETH → receives X + Y ETH, profiting Y ETH.

## Impact Explanation
This is **direct theft of user funds** — a Critical impact. The victim's deposited ETH is permanently locked in the pool (or redeemable only by the attacker), with no mechanism for the victim to recover it. The attacker profits by the full amount of the victim's deposit.

## Likelihood Explanation
All three preconditions are realistic:
1. **First-depositor state**: Occurs at protocol launch or after a full withdrawal cycle. No front-running required; the attacker sets up the inflated state in advance.
2. **`pricePercentageLimit == 0`**: This is the **default state** since `initialize()` never sets it. The protocol is vulnerable from deployment until an admin explicitly calls `setPricePercentageLimit`.
3. **`minRSETHAmountExpected = 0`**: Common in integrator scripts, bots, and UI defaults that omit slippage protection.

The attack requires only a small ETH donation (e.g., 2 ETH to steal a 1 ETH deposit), making it economically feasible.

## Recommendation
1. **Virtual offset / dead shares**: Mint a small amount of rsETH (e.g., 1000 wei) to a dead address at initialization so the supply is never 1 wei, making the rounding attack economically infeasible.
2. **Exclude donations from TVL**: Track deposited ETH in a separate accounting variable rather than using `address(this).balance` directly in `getETHDistributionData()`.
3. **Set `pricePercentageLimit` at initialization**: Assign a non-zero default in `initialize()` so the price-increase guard is always active from deployment.
4. **Reject zero-rsETH mints unconditionally**: In `_beforeDeposit`, revert if `rsethAmountToMint == 0` regardless of `minRSETHAmountExpected`.

## Proof of Concept
```
State: rsETH totalSupply = 0, pricePercentageLimit = 0 (default)

1. updateRSETHPrice() → rsETHPrice = 1e18 (zero-supply branch, LRTOracle.sol:218-222)

2. Attacker: depositETH{value: 1}(0, "")
   → rsethAmountToMint = 1 * 1e18 / 1e18 = 1
   → Attacker holds 1 wei rsETH; LRTDepositPool.balance = 1 wei

3. Attacker sends 2e18 ETH directly to LRTDepositPool (receive())
   → LRTDepositPool.balance = 2e18 + 1

4. Attacker: updateRSETHPrice()
   → totalETHInProtocol ≈ 2e18 (via address(this).balance, LRTDepositPool.sol:480)
   → rsethSupply = 1
   → rsETHPrice = 2e18 * 1e18 / 1 = 2e36

5. Victim: depositETH{value: 1e18}(0, "")
   → rsethAmountToMint = 1e18 * 1e18 / 2e36 = 0
   → minRSETHAmountExpected = 0 → 0 < 0 is false → no revert (LRTDepositPool.sol:667)
   → Victim's 1e18 ETH absorbed, 0 rsETH minted

6. Attacker redeems 1 wei rsETH via withdrawal
   → Receives ≈ 3e18 ETH (2e18 donated + 1 wei deposit + 1e18 victim deposit)
   → Net profit: 1e18 ETH (victim's deposit)
```

Foundry test plan: deploy `LRTDepositPool` + `LRTOracle` with `pricePercentageLimit = 0`, execute the above sequence as two separate EOAs, assert victim's rsETH balance is 0 and attacker's redeemed ETH equals initial donation + victim deposit.