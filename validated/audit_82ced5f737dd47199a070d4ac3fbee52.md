Audit Report

## Title
`PriceVelocityGuardExtension` Uses `block.number` Instead of `block.timestamp`, Making the Velocity Guard Chain-Dependent — (File: `metric-periphery/contracts/extensions/PriceVelocityGuardExtension.sol`)

## Summary
`PriceVelocityGuardExtension.beforeSwap` and `setLastMidPrice` both record elapsed time using `block.number`, computing the allowed price-change budget as `maxChangePerBlockE18² × (1 + blockDiff)`. Because block production rates differ across EVM chains (Ethereum ~12 s, BSC ~3 s, Avalanche ~1 s), the effective per-real-time-second allowance diverges from the admin's intent. On fast-block chains the guard is far more permissive than intended (enabling bad-price execution); on slow-block chains it is far more restrictive than intended (breaking core swap functionality).

## Finding Description
In `beforeSwap`, the contract reads `prevBlock = s.lastUpdateBlock`, then writes `s.lastUpdateBlock = uint64(block.number)` and computes:

```solidity
uint256 blockDiff = block.number - prevBlock;
uint256 allowedSq = uint256(maxChange) * uint256(maxChange) * (1 + blockDiff);
``` [1](#0-0) 

`setLastMidPrice` similarly writes `s.lastUpdateBlock = uint64(block.number)`, so the reference point is always block-indexed. [2](#0-1) 

The parameter `maxChangePerBlockE18` is calibrated by the pool admin as a per-block cap. An admin targeting Ethereum (12 s/block) who sets `maxChangePerBlockE18 = X` to allow `X%` per 12 seconds will, on Avalanche (1 s/block), allow `X%` per 1 second — a 12× looser guard per unit of real time. On a slow-block L2 (e.g., 60 s/block), the same value allows only `X%` per 60 seconds, causing `PriceVelocityExceeded` reverts on legitimate oracle updates.

The protocol explicitly targets multi-chain deployment: L1 and L2 deployment scripts exist under `smart-contracts-poc/script/l1/` and `smart-contracts-poc/script/l2/`.



By contrast, the existing staleness check in `PriceProvider._isStale` correctly uses `block.timestamp` and a `maxDelta` in seconds, making it chain-agnostic. [3](#0-2) 

No existing guard compensates for chain-specific block times; the admin has no on-chain mechanism to query the chain's block interval, so miscalibration is the default outcome on any non-Ethereum deployment.

## Impact Explanation
**Fast-block chains (BSC 3 s, Avalanche 1 s):** The velocity guard is 4–12× more permissive per real-time second than intended. Oracle prices that have moved far beyond the intended safety envelope pass the guard, and swaps execute at those prices — a bad-price execution failure where the pool pays out more tokens than the safety envelope permits.

**Slow-block chains (some L2s):** The guard is proportionally tighter. Legitimate oracle price updates reflecting real market moves trigger `PriceVelocityExceeded`, reverting every swap until the admin manually resets `lastMidPrice` via `setLastMidPrice`. This breaks core pool swap functionality for all unprivileged traders.

Both outcomes fall within the allowed impact gate: bad-price execution (fast chains) and broken core pool functionality causing unusable swap flows (slow chains).

## Likelihood Explanation
The protocol is designed for multi-chain deployment (L1 and L2 scripts confirmed). Any pool that enables `PriceVelocityGuardExtension` on a non-Ethereum chain is affected by default. The admin who sets `maxChangePerBlockE18` has no on-chain mechanism to determine the chain's block time, making miscalibration the expected outcome rather than an edge case. The extension is a first-class periphery contract, not a test mock, and `beforeSwap` is called on every swap.

## Recommendation
Replace `block.number` with `block.timestamp` throughout `PriceVelocityGuardExtension`. Rename the storage field `lastUpdateBlock` to `lastUpdateTimestamp` and the parameter to `maxChangePerSecondE18`. Update the formula:

```solidity
uint256 timeDiff = block.timestamp - s.lastUpdateTimestamp;
uint256 allowedSq = uint256(maxChange) * uint256(maxChange) * (1 + timeDiff);
```

Store `lastUpdateTimestamp` as a `uint64` (seconds since epoch fits comfortably for centuries). This makes the guard chain-agnostic and consistent with how `PriceProvider._isStale` already measures staleness using `block.timestamp` and `MAX_TIME_DELTA` in seconds.

## Proof of Concept
**Setup:** Deploy `PriceVelocityGuardExtension` on Avalanche (1 s/block). Admin sets `maxChangePerBlockE18 = 1e15` (0.1% per block, intending 0.1% per 12 s on Ethereum).

**On Avalanche:** 60 blocks pass in 60 seconds.
```
blockDiff = 60
allowedSq = (1e15)² × 61 = 6.1e31
sqrt(allowedSq) / 1e18 ≈ 7.8%  ← allowed change in 60 real seconds
```

**On Ethereum:** 5 blocks pass in 60 seconds.
```
blockDiff = 5
allowedSq = (1e15)² × 6 = 6e30
sqrt(allowedSq) / 1e18 ≈ 2.4%  ← allowed change in 60 real seconds
```

A Foundry fork test against an Avalanche RPC can confirm: roll the fork forward 60 blocks, call `beforeSwap` with a mid-price 5% above `lastMidPriceX64`, and observe the call succeeds (no `PriceVelocityExceeded` revert) — whereas the identical test on an Ethereum fork at 5 blocks elapsed reverts. The identical configuration produces a 3.2× difference in allowed real-time price movement, with the Avalanche deployment permitting swaps at oracle prices that would be blocked on Ethereum.

### Citations

**File:** metric-periphery/contracts/extensions/PriceVelocityGuardExtension.sol (L29-34)
```text
  function setLastMidPrice(address pool_, uint128 newLastMidPriceX64) external onlyPoolAdmin(pool_) {
    PriceVelocityState storage s = priceVelocityState[pool_];
    s.lastMidPriceX64 = newLastMidPriceX64;
    s.lastUpdateBlock = uint64(block.number);
    emit LastMidPriceUpdated(pool_, newLastMidPriceX64);
  }
```

**File:** metric-periphery/contracts/extensions/PriceVelocityGuardExtension.sol (L55-70)
```text
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
```

**File:** smart-contracts-poc/contracts/PriceProvider.sol (L125-133)
```text
    function _isStale(
        uint256 refTime,
        uint256 nowTs,
        uint256 maxDelta
    ) internal pure returns (bool) {
        if (refTime == 0) return true;
        if (refTime > nowTs) return true;
        return (nowTs - refTime) > maxDelta;
    }
```
