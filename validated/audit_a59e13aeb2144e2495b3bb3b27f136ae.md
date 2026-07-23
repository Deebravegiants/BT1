### Title
USDC-Blacklisted LP Permanently Loses Principal: `removeLiquidity` Hardcodes Transfer to `owner` With No Alternative Recipient - (File: `metric-core/contracts/libraries/LiquidityLib.sol`)

---

### Summary

`LiquidityLib.removeLiquidity` unconditionally transfers withdrawn tokens directly to the position `owner` address. If the pool contains USDC (or USDT) and the LP's address is later blacklisted by the USDC contract, every call to `removeLiquidity` reverts at the `safeTransfer` step. Because the function also enforces `msg.sender == owner` and provides no alternative-recipient parameter, the LP has no recovery path: their principal is permanently locked inside the pool.

---

### Finding Description

`MetricOmmPool.removeLiquidity` delegates to `LiquidityLib.removeLiquidity`, which computes the token amounts owed to the LP and then transfers them:

```solidity
// metric-core/contracts/libraries/LiquidityLib.sol  lines 242-247
if (amount0Removed > 0) {
    IERC20(ctx.token0).safeTransfer(owner, amount0Removed);
}
if (amount1Removed > 0) {
    IERC20(ctx.token1).safeTransfer(owner, amount1Removed);
}
``` [1](#0-0) 

The caller is gated by `msg.sender != owner` in the pool:

```solidity
// metric-core/contracts/MetricOmmPool.sol  line 206
if (msg.sender != owner) revert NotPositionOwner();
``` [2](#0-1) 

There is no `recipient` parameter, no emergency-withdrawal path, and no mechanism to transfer a position to a different address. LP positions are keyed by `keccak256(abi.encode(owner, salt, bin))`, so the position is permanently bound to the blacklisted address. [3](#0-2) 

USDC's `transfer` reverts when the recipient is on its blacklist. Because `safeTransfer` wraps this call and propagates the revert, the entire `removeLiquidity` transaction fails. The bin-state and share accounting updates that precede the transfer are rolled back, so the LP's shares remain intact but permanently unreachable.

---

### Impact Explanation

An LP who provided liquidity to a USDC pool and is subsequently blacklisted by Circle loses 100% of their deposited principal with no on-chain recovery path. The funds remain in the pool indefinitely, effectively becoming unclaimable dead weight. This is a direct, permanent loss of user principal — the highest-severity outcome under the Allowed Impact Gate.

---

### Likelihood Explanation

USDC blacklisting is a documented, exercised mechanism (Circle has blacklisted hundreds of addresses). Any LP in any USDC-paired Metric OMM pool is exposed. The LP need not be malicious; regulatory action, sanctions, or exchange-level compliance events can trigger blacklisting after the LP has already deposited. The condition is therefore realistic and unprivileged from the protocol's perspective.

---

### Recommendation

Add an optional `recipient` parameter to `removeLiquidity` (analogous to the `recipient` parameter already present on `swap`). When provided, transfer withdrawn tokens to `recipient` instead of `owner`. The `msg.sender == owner` check still enforces that only the position owner can initiate the withdrawal; the owner simply directs the proceeds to a non-blacklisted address:

```solidity
function removeLiquidity(
    address owner,
    address recipient,   // <-- new
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata extensionData
) external ...
```

Inside `LiquidityLib.removeLiquidity`, replace `safeTransfer(owner, ...)` with `safeTransfer(recipient, ...)`. This mirrors the pattern already used in `swap` where output tokens are sent to a caller-specified `recipient` rather than `msg.sender`. [4](#0-3) 

---

### Proof of Concept

1. Alice provides liquidity to a USDC/WETH Metric OMM pool by calling `addLiquidity`. Her position is recorded under `keccak256(abi.encode(alice, salt, bin))`.
2. Circle blacklists Alice's address (e.g., due to a regulatory freeze).
3. Alice calls `removeLiquidity(alice, salt, deltas, "")`. The pool enforces `msg.sender == owner == alice` — passes.
4. `LiquidityLib.removeLiquidity` computes `amount1Removed > 0` (USDC owed) and calls `IERC20(usdc).safeTransfer(alice, amount1Removed)`.
5. USDC's `transfer` reverts because `alice` is blacklisted. The entire transaction reverts.
6. Alice's shares remain in the pool. She cannot specify a different recipient. She cannot transfer her position. Her USDC principal is permanently locked. [5](#0-4)

### Citations

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L161-251)
```text
  function removeLiquidity(
    PoolContext memory ctx,
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    BinTotals storage binTotals,
    mapping(int256 => BinState) storage binStates,
    mapping(int256 => uint256) storage binTotalShares,
    mapping(bytes32 => uint256) storage positionBinShares
  ) public returns (uint256 amount0Removed, uint256 amount1Removed) {
    unchecked {
      uint256 length = deltas.binIdxs.length;
      if (length == 0) return (0, 0);

      uint256 totalToken0ToRemoveScaled = 0;
      uint256 totalToken1ToRemoveScaled = 0;

      BinBalanceDelta[] memory binBalanceDeltas = new BinBalanceDelta[](length);

      for (uint256 i = 0; i < length; i++) {
        int256 binIdx = deltas.binIdxs[i];
        uint256 sharesToRemove = deltas.shares[i];

        if (binIdx < ctx.lowestBin || binIdx > ctx.highestBin) {
          revert IMetricOmmPoolActions.InvalidBinIndex(binIdx);
        }
        if (sharesToRemove == 0) continue;

        {
          // safe because -128 <= LOWEST_BIN <= HIGHEST_BIN <= 127 (enforced by factory)
          // forge-lint: disable-next-line(unsafe-typecast)
          bytes32 posKey = _positionBinKey(owner, salt, int8(binIdx));
          uint256 binTotalSharesVal = binTotalShares[binIdx];
          uint256 userShares = positionBinShares[posKey];

          if (userShares < sharesToRemove) {
            revert IMetricOmmPoolActions.InsufficientLiquidity(sharesToRemove, userShares);
          }
          uint256 newUserShares = userShares - sharesToRemove;
          if (newUserShares > 0 && newUserShares < ctx.minimalMintableLiquidity) {
            revert IMetricOmmPoolActions.MinimalLiquidity(newUserShares, ctx.minimalMintableLiquidity);
          }

          BinState storage binState = binStates[binIdx];
          uint256 amount0Scaled = _checkedMul(binState.token0BalanceScaled, sharesToRemove) / binTotalSharesVal;
          uint256 amount1Scaled = _checkedMul(binState.token1BalanceScaled, sharesToRemove) / binTotalSharesVal;

          // casting to uint104 is safe because amount0Scaled and amount1Scaled are less than token(0|1)BalanceScaled
          // forge-lint: disable-next-line(unsafe-typecast)
          binState.token0BalanceScaled -= uint104(amount0Scaled);
          // forge-lint: disable-next-line(unsafe-typecast)
          binState.token1BalanceScaled -= uint104(amount1Scaled);
          binTotalShares[binIdx] = binTotalSharesVal - sharesToRemove;
          positionBinShares[posKey] = newUserShares;

          totalToken0ToRemoveScaled += amount0Scaled;
          totalToken1ToRemoveScaled += amount1Scaled;

          binBalanceDeltas[i] = BinBalanceDelta({
            // safe because amount0Scaled is bounded by uint104 bin balances.
            // forge-lint: disable-next-line(unsafe-typecast)
            delta0Scaled: -int256(amount0Scaled),
            // safe because amount1Scaled is bounded by uint104 bin balances.
            // forge-lint: disable-next-line(unsafe-typecast)
            delta1Scaled: -int256(amount1Scaled)
          });
        }
      }

      if (totalToken0ToRemoveScaled > 0) {
        // forge-lint: disable-next-line(unsafe-typecast)
        binTotals.scaledToken0 = uint128(uint256(binTotals.scaledToken0) - totalToken0ToRemoveScaled);
      }
      if (totalToken1ToRemoveScaled > 0) {
        // forge-lint: disable-next-line(unsafe-typecast)
        binTotals.scaledToken1 = uint128(uint256(binTotals.scaledToken1) - totalToken1ToRemoveScaled);
      }

      (amount0Removed, amount1Removed) =
        _deltasScaledToExternal(totalToken0ToRemoveScaled, totalToken1ToRemoveScaled, ctx, Math.Rounding.Floor);

      if (amount0Removed > 0) {
        IERC20(ctx.token0).safeTransfer(owner, amount0Removed);
      }
      if (amount1Removed > 0) {
        IERC20(ctx.token1).safeTransfer(owner, amount1Removed);
      }

      emit IMetricOmmPoolActions.LiquidityRemoved(owner, salt, deltas.binIdxs, binBalanceDeltas, deltas.shares);
    }
  }
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L256-259)
```text
  function _positionBinKey(address owner, uint80 salt, int8 bin) internal pure returns (bytes32 key) {
    // forge-lint: disable-next-line(asm-keccak256)
    return keccak256(abi.encode(owner, salt, bin));
  }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L199-212)
```text
  function removeLiquidity(address owner, uint80 salt, LiquidityDelta calldata deltas, bytes calldata extensionData)
    external
    nonReentrant(PoolActions.REMOVE_LIQUIDITY)
    returns (uint256 amount0Removed, uint256 amount1Removed)
  {
    if (deltas.binIdxs.length == 0) return (0, 0);
    if (deltas.binIdxs.length != deltas.shares.length) revert LiquidityDeltaLengthMismatch();
    if (msg.sender != owner) revert NotPositionOwner();
    _beforeRemoveLiquidity(msg.sender, owner, salt, deltas, extensionData);
    (amount0Removed, amount1Removed) = LiquidityLib.removeLiquidity(
      _liquidityContext(), owner, salt, deltas, binTotals, _binStates, _binTotalShares, _positionBinShares
    );
    _afterRemoveLiquidity(msg.sender, owner, salt, deltas, amount0Removed, amount1Removed, extensionData);
  }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L250-268)
```text
    if (zeroForOne) {
      if (amount1Delta < 0) {
        // casting to uint256 is safe because amount1Delta is negative and the ammount of tokens in pool is capped by uint128.max
        // forge-lint: disable-next-line(unsafe-typecast)
        transferToken1(recipient, uint256(-amount1Delta));
      }

      uint256 balance0Before = balance0();
      IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData);
      // casting to uint256 is safe because amount0Delta is positive and the ammount of tokens in pool is capped by uint128.max
      // forge-lint: disable-next-line(unsafe-typecast)
      if (amount0Delta > 0 && balance0Before + uint256(amount0Delta) > balance0()) {
        revert IncorrectDelta();
      }
    } else {
      if (amount0Delta < 0) {
        // casting to uint256 is safe because amount0Delta is negative and the ammount of tokens in pool is capped by uint128.max
        // forge-lint: disable-next-line(unsafe-typecast)
        transferToken0(recipient, uint256(-amount0Delta));
```
