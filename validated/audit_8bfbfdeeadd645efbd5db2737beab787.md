### Title
`PriceVelocityGuardExtension` per-block velocity cap is enforced per-swap rather than per-block, allowing cumulative oracle price drift to multiply the intended limit within a single block — (`File: metric-periphery/contracts/extensions/PriceVelocityGuardExtension.sol`)

---

### Summary

`PriceVelocityGuardExtension.beforeSwap()` updates `lastMidPriceX64` and `lastUpdateBlock` on **every swap invocation** before performing the velocity check. When multiple swaps occur in the same block with incrementally shifting oracle prices, each swap passes the check individually against the prior swap's price (not the block's opening price), allowing the cumulative intra-block price movement to reach `N × maxChangePerBlockE18` for `N` swaps — the exact same per-user-vs-global accounting error as M-04.

---

### Finding Description

The extension's stated invariant (NatSpec, lines 15–17) is:

```
changeE18^2 <= maxChangePerBlockE18^2 * (1 + blockDiff)
```

where `blockDiff = block.number - lastUpdateBlock`. The intent is that the oracle mid-price cannot move more than `maxChangePerBlockE18` per block.

The implementation in `beforeSwap` (lines 57–58) **writes the new price and block number into storage before the check**:

```solidity
s.lastMidPriceX64 = midPrice;          // ← state mutated first
s.lastUpdateBlock = uint64(block.number); // ← state mutated first

if (prevMid != 0) {
    ...
    uint256 blockDiff = block.number - prevBlock;
    ...
    if (actualSq > allowedSq) revert PriceVelocityExceeded(...);
}
```

When two or more swaps land in the same block with different oracle prices:

| Swap | `prevBlock` | `blockDiff` | Price checked against | Passes? |
|------|-------------|-------------|----------------------|---------|
| 1 (block N) | B_old | N − B_old | P0 → P1 (≤ maxChange) | ✓ |
| 2 (block N) | **N** | **0** | P1 → P2 (≤ maxChange) | ✓ |
| 3 (block N) | **N** | **0** | P2 → P3 (≤ maxChange) | ✓ |

Each swap is checked against the **previous swap's price**, not the block's opening price. The cumulative movement P0 → P3 ≈ 3 × maxChangePerBlockE18 in one block, violating the invariant the guard was designed to enforce.

---

### Impact Explanation

The velocity guard's security guarantee is broken. An attacker (or a Pyth price-update submitter, since Pyth allows anyone to push a signed price update) can:

1. Submit oracle price update P0 → P1 (within `maxChange`).
2. Call `swap()` → guard passes, `lastMidPriceX64 = P1`.
3. Submit oracle price update P1 → P2 (within `maxChange`).
4. Call `swap()` → guard passes, `lastMidPriceX64 = P2`.
5. Repeat N times in the same block.

The pool executes swaps at oracle prices that the velocity guard was supposed to block. LPs are exposed to bad-price execution — they sell tokens at a price far from the true market mid, suffering direct principal loss. This matches the allowed impact gate: **bad-price execution: unclamped bid/ask quote reaches a pool swap**.

---

### Likelihood Explanation

Pyth oracle prices are updated by submitting signed VAA payloads; any on-chain actor can submit a valid signed update. On chains where multiple Pyth updates are available within the same block (common on fast L2s), an attacker can chain price updates and swaps atomically in a single transaction or across multiple transactions in the same block. The attack requires no privileged role and no malicious pool setup.

---

### Recommendation

Only advance `lastMidPriceX64` when entering a **new block**. Within the same block, keep the stored price fixed so every swap is checked against the block's opening price:

```solidity
if (block.number > prevBlock) {
    // New block: record the opening price for this block
    s.lastMidPriceX64 = midPrice;
    s.lastUpdateBlock = uint64(block.number);
} 
// If same block: do NOT update lastMidPriceX64; check current price against block-open price

if (prevMid != 0) {
    uint256 blockDiff = block.number - prevBlock;
    // ... existing check unchanged ...
}
```

This ensures all swaps within the same block are bounded against the same reference price, matching the documented invariant.

---

### Proof of Concept

```
Setup:
  maxChangePerBlockE18 = 0.05e18  (5% per block)
  lastMidPriceX64 = P0 = 1e18    (set in block B_old)

Block N (attacker bundles 3 swaps + 2 Pyth updates):

  Tx1: Pyth update → oracle price = P1 = 1.05e18 (+5%)
  Tx2: swap() → beforeSwap called
       prevMid = P0, prevBlock = B_old, blockDiff = N - B_old
       changeE18 = 5%, actualSq = (0.05e18)^2
       allowedSq = (0.05e18)^2 * (1 + blockDiff) ≥ actualSq  → PASS
       lastMidPriceX64 = P1, lastUpdateBlock = N

  Tx3: Pyth update → oracle price = P2 = 1.1025e18 (+5% from P1)
  Tx4: swap() → beforeSwap called
       prevMid = P1, prevBlock = N, blockDiff = 0
       changeE18 = 5%, actualSq = (0.05e18)^2
       allowedSq = (0.05e18)^2 * 1 = actualSq  → PASS (boundary)
       lastMidPriceX64 = P2, lastUpdateBlock = N

  Tx5: Pyth update → oracle price = P3 = 1.1576e18 (+5% from P2)
  Tx6: swap() → beforeSwap called
       prevMid = P2, prevBlock = N, blockDiff = 0
       changeE18 = 5%  → PASS
       lastMidPriceX64 = P3

Result:
  Total price movement in block N: P0 → P3 = +15.76%
  Intended per-block cap:          5%
  Guard bypassed by factor:        ~3×
  LPs execute swaps at P3, which is 10.76% above the guard's intended ceiling.
``` [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** metric-periphery/contracts/extensions/PriceVelocityGuardExtension.sol (L9-18)
```text
/// @title PriceVelocityGuardExtension
/// @notice Caps how fast the provided price can move between blocks, per pool.
/// @dev This extension allows the pool admin to increase security of the pool by limiting price
///      manipulation through velocity constraints. However, it assumes that the pool admin is not
///      an adversary and acts to optimize pool profitability. The pool admin must be trusted.
///
///      Allowed deviation scales as `maxChangePerBlockE18 * sqrt(1 + blockDifference)`.
///      Comparison is performed on squares to avoid an on-chain sqrt:
///        changeE18^2 <= maxChangePerBlockE18^2 * (1 + blockDiff)
///      where 1e18 = 100% (full unit).
```

**File:** metric-periphery/contracts/extensions/PriceVelocityGuardExtension.sol (L53-76)
```text
    PriceVelocityState storage s = priceVelocityState[pool_];
    uint128 prevMid = s.lastMidPriceX64;
    uint64 prevBlock = s.lastUpdateBlock;

    s.lastMidPriceX64 = midPrice;
    s.lastUpdateBlock = uint64(block.number);

    if (prevMid != 0) {
      uint64 maxChange = s.maxChangePerBlockE18;
      if (maxChange != 0) {
        uint256 blockDiff = block.number - prevBlock;

        uint256 delta = midPrice > prevMid ? uint256(midPrice - prevMid) : uint256(prevMid - midPrice);

        uint256 changeE18 = (delta * 1e18) / uint256(prevMid);

        uint256 actualSq = changeE18 * changeE18;
        uint256 allowedSq = uint256(maxChange) * uint256(maxChange) * (1 + blockDiff);

        if (actualSq > allowedSq) {
          revert PriceVelocityExceeded(actualSq, allowedSq);
        }
      }
    }
```

**File:** metric-periphery/contracts/interfaces/extensions/IPriceVelocityGuardExtension.sol (L7-11)
```text
  struct PriceVelocityState {
    uint128 lastMidPriceX64;
    uint64 lastUpdateBlock;
    uint64 maxChangePerBlockE18;
  }
```
