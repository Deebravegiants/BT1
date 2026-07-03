Audit Report

## Title
rsETH Share Inflation Attack via Asset Donation Inflates `rsETHPrice`, Causing Zero-Share Deposits - (File: contracts/LRTOracle.sol / contracts/LRTDepositPool.sol)

## Summary
An attacker who is the first depositor can donate LST tokens directly to `LRTDepositPool`, then call the public `updateRSETHPrice()` to inflate the stored `rsETHPrice` to an astronomically large value. Because `_beforeDeposit` does not guard against `rsethAmountToMint == 0`, subsequent depositors who pass `minRSETHAmountExpected = 0` lose their entire deposit while receiving zero rsETH. The attacker's single wei of rsETH then represents the entire pool, enabling theft of all victim deposits.

## Finding Description

**Root cause 1 — `balanceOf`-based accounting includes donations:**
`getAssetDistributionData` uses `IERC20(asset).balanceOf(address(this))` at `LRTDepositPool.sol:444` to measure assets in the pool. Any direct token transfer (donation) to the pool is immediately reflected in `getTotalAssetDeposits`, which feeds `_getTotalEthInProtocol` at `LRTOracle.sol:341`.

**Root cause 2 — `updateRSETHPrice()` is public with no effective price guard:**
`LRTOracle.sol:87` exposes `updateRSETHPrice()` to any caller. The price-increase guard at `LRTOracle.sol:256–257` is:
```solidity
bool isPriceIncreaseOffLimit =
    pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
```
`pricePercentageLimit` is declared at `LRTOracle.sol:29` and is never set in `initialize` (`LRTOracle.sol:64–68`), so it defaults to `0`. The short-circuit makes `isPriceIncreaseOffLimit = false` regardless of the price jump magnitude.

**Root cause 3 — `_beforeDeposit` does not reject zero-share mints:**
`LRTDepositPool.sol:665–669` computes `rsethAmountToMint` and only checks `rsethAmountToMint < minRSETHAmountExpected`. When `minRSETHAmountExpected == 0` and `rsethAmountToMint == 0`, the condition `0 < 0` is false and no revert occurs. The victim's assets are transferred in and `IRSETH.mint(victim, 0)` is called, which succeeds silently (OpenZeppelin `_mint` does not revert on amount 0).

**Exploit path:**
1. Attacker calls `depositAsset(stETH, 1 wei, 0, "")` → 1 wei rsETH minted; `rsethSupply = 1`.
2. Attacker calls `stETH.transfer(depositPool, 1e18)` → `balanceOf(depositPool) ≈ 1e18`; no rsETH minted.
3. Attacker calls `lrtOracle.updateRSETHPrice()` → `totalETHInProtocol ≈ 1e18`; `newRsETHPrice = 1e18 * 1e18 / 1 = 1e36`; guard bypassed (`pricePercentageLimit == 0`); `rsETHPrice = 1e36`.
4. Victim calls `depositAsset(stETH, 0.5e18, 0, "")` → `rsethAmountToMint = (0.5e18 * 1e18) / 1e36 = 0`; `0 < 0` is false; 0.5e18 stETH transferred from victim; 0 rsETH minted.
5. Attacker calls `updateRSETHPrice()` again → `totalETHInProtocol ≈ 1.5e18`; attacker's 1 wei rsETH is now redeemable for 1.5 ETH worth of assets.

**Why existing checks fail:**
- `minAmountToDeposit` defaults to 0, so 1-wei deposits pass `LRTDepositPool.sol:657`.
- `checkDailyMintLimit` in `RSETH.sol:50` only blocks minting when `amount > maxMintAmountPerDay`; minting 0 always passes, and the attacker's 1-wei mint passes once `maxMintAmountPerDay` is set to any non-zero value (required for the protocol to function).
- `_checkIfDepositAmountExceedesCurrentLimit` at `LRTDepositPool.sol:676–682` checks against `depositLimitByAsset`, which must be set above zero for the protocol to accept any deposits; the donated amount counts against this limit but does not block the victim's deposit if the limit is set generously.

## Impact Explanation

**Critical — Direct theft of any user funds.**

Any victim who calls `depositAsset` or `depositETH` with `minRSETHAmountExpected = 0` (the common default for integrators and naive users) after the price has been inflated loses their entire deposit. The attacker redeems the stolen value by holding the only rsETH in existence. The impact is concrete and repeatable: every subsequent victim deposit increases the attacker's redemption value.

## Likelihood Explanation

- `pricePercentageLimit` is `0` by default and is not initialized in `initialize`, so the price guard is inactive on every fresh deployment until an admin explicitly calls `setPricePercentageLimit`.
- `updateRSETHPrice()` is callable by any unprivileged address with no role restriction.
- Direct token transfers to `LRTDepositPool` are fully reflected in `getTotalAssetDeposits` via raw `balanceOf`.
- The attack is most effective at protocol launch (low rsETH supply) or after a large burn event reduces supply to near zero.
- Users and integrators commonly pass `minRSETHAmountExpected = 0` as a default, making them fully exposed.
- The attacker's cost is the donated amount (1 ETH in the PoC), which is fully recovered after the attack.

## Recommendation

1. **Reject zero-share mints** in `_beforeDeposit` (`LRTDepositPool.sol:648`):
   ```solidity
   if (rsethAmountToMint == 0) revert ZeroRsETHMinted();
   ```

2. **Set `pricePercentageLimit` in `initialize`** (`LRTOracle.sol:64`): provide a safe non-zero default (e.g., `1e16` for 1%) so the price guard is active from deployment.

3. **Minimum initial deposit / dead shares**: On the first deposit, mint a small amount of rsETH to the zero address to prevent the 1-wei rsETH scenario.

4. **Snapshot-based accounting**: Replace raw `balanceOf` in `getAssetDistributionData` with an internal accounting variable updated only through deposit/withdrawal functions, making donations invisible to the price oracle.

## Proof of Concept

```
Preconditions:
  - Protocol freshly deployed; pricePercentageLimit == 0 (default)
  - maxMintAmountPerDay set to any non-zero value (required for protocol to function)
  - depositLimitByAsset(stETH) set above 1.5e18 (required for protocol to accept deposits)
  - rsETHPrice == 1e18 (set when totalSupply was 0)

Step 1: Attacker calls depositAsset(stETH, 1, 0, "")
  → rsethAmountToMint = (1 * 1e18) / 1e18 = 1
  → 1 wei rsETH minted to attacker; rsethSupply = 1

Step 2: Attacker calls stETH.transfer(depositPool, 1e18)
  → depositPool.balanceOf(stETH) = 1 + 1e18 ≈ 1e18
  → rsethSupply still = 1

Step 3: Attacker calls lrtOracle.updateRSETHPrice()
  → totalETHInProtocol ≈ 1e18 (via balanceOf)
  → newRsETHPrice = 1e18 * 1e18 / 1 = 1e36
  → pricePercentageLimit == 0 → isPriceIncreaseOffLimit = false → guard bypassed
  → rsETHPrice = 1e36

Step 4: Victim calls depositAsset(stETH, 0.5e18, 0, "")
  → rsethAmountToMint = (0.5e18 * 1e18) / 1e36 = 0
  → 0 < 0 is false → no revert
  → 0.5e18 stETH transferred from victim; IRSETH.mint(victim, 0) → no-op
  → victim receives 0 rsETH

Step 5: Attacker calls updateRSETHPrice()
  → totalETHInProtocol ≈ 1.5e18
  → rsETHPrice = 1.5e36
  → Attacker's 1 wei rsETH redeemable for 1.5 ETH worth of assets (victim's 0.5 ETH stolen)

Foundry test plan:
  - Deploy LRTConfig, LRTOracle, LRTDepositPool, RSETH with mock stETH and price oracle
  - Set maxMintAmountPerDay to type(uint256).max; set depositLimitByAsset(stETH) to 100e18
  - Execute Steps 1–5 above
  - Assert: victim rsETH balance == 0; attacker can redeem for > 1e18 stETH
```