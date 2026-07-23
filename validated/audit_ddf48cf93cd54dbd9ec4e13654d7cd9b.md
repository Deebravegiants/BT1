### Title
LP Funds Permanently Locked When Owner Is USDC/USDT Blacklisted in `removeLiquidity` — (File: metric-core/contracts/libraries/LiquidityLib.sol)

---

### Summary

`LiquidityLib.removeLiquidity` unconditionally pushes withdrawn tokens to the `owner` address with no alternative recipient path. If `owner` is blacklisted by USDC or USDT after depositing, every future `removeLiquidity` call reverts, permanently locking the LP's principal with no recovery mechanism.

---

### Finding Description

In `LiquidityLib.removeLiquidity`, after all internal state is updated (bin balances decremented, shares burned, `binTotals` reduced), the function performs direct push transfers to `owner`:

```solidity
// LiquidityLib.sol lines 242–247
if (amount0Removed > 0) {
    IERC20(ctx.token0).safeTransfer(owner, amount0Removed);
}
if (amount1Removed > 0) {
    IERC20(ctx.token1).safeTransfer(owner, amount1Removed);
}
``` [1](#0-0) 

`MetricOmmPool.removeLiquidity` enforces `msg.sender == owner`, so the position owner must be the caller, and the tokens are always sent to that same address — there is no `recipient` parameter:

```solidity
// MetricOmmPool.sol line 206
if (msg.sender != owner) revert NotPositionOwner();
``` [2](#0-1) 

Because all state mutations (bin balance decrements, share burns, `binTotals` updates) occur inside the same transaction before the transfers, a revert on `safeTransfer` rolls back every state change. The LP's position is left intact but permanently inaccessible: every subsequent call to `removeLiquidity` will hit the same revert. Positions are keyed by `keccak256(abi.encode(owner, salt, bin))` and are not transferable, so there is no escape hatch. [3](#0-2) 

---

### Impact Explanation

The LP's entire deposited principal is permanently locked inside the pool. The `removeLiquidity` flow becomes completely unusable for the affected address. This satisfies two impact-gate criteria simultaneously: *direct loss of user principal* and *unusable withdraw/liquidity flow*.

---

### Likelihood Explanation

USDC and USDT both implement on-chain address blacklists enforced at the token level. An LP can be blacklisted after depositing (e.g., regulatory action, sanctions compliance, or erroneous listing). The probability per individual LP is low, but the consequence is irreversible and total. USDC/USDT blacklisting is explicitly within scope per the contest rules.

---

### Recommendation

Add an optional `recipient` parameter to `removeLiquidity` so the position owner can direct withdrawn tokens to an address they control that is not blacklisted:

```solidity
function removeLiquidity(
    address owner,
    address recipient,   // <-- new
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata extensionData
) external ...
```

Then transfer to `recipient` instead of `owner`. Alternatively, implement a pull pattern: store owed amounts in an internal mapping keyed by `owner` and expose a separate `claim(address recipient)` function.

---

### Proof of Concept

1. Pool is deployed with USDC as `token0`.
2. Alice (`owner = alice`) calls `addLiquidity`; her shares are recorded under `keccak256(abi.encode(alice, salt, bin))`.
3. USDC blacklists Alice's address.
4. Alice calls `removeLiquidity(alice, salt, deltas, "")`.
5. `MetricOmmPool` passes `owner = alice` into `LiquidityLib.removeLiquidity`.
6. The library computes `amount0Removed > 0` and executes `IERC20(USDC).safeTransfer(alice, amount0Removed)`.
7. USDC reverts because `alice` is blacklisted.
8. The entire transaction reverts; all state changes are rolled back.
9. Alice's position remains in storage but every future `removeLiquidity` call produces the same revert — her funds are permanently locked. [4](#0-3) [5](#0-4)

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
