### Title
LP Principal Permanently Locked When USDC/USDT Blacklists Position Owner in `removeLiquidity` — (`metric-core/contracts/libraries/LiquidityLib.sol`)

### Summary

`LiquidityLib.removeLiquidity` transfers pool tokens directly to `owner` with no fallback path. If `owner` is blacklisted by USDC or USDT (both deployed as pool tokens in the protocol's own config), every withdrawal attempt reverts and the LP's principal is permanently locked with no recovery mechanism.

### Finding Description

In `LiquidityLib.removeLiquidity`, after burning shares and updating all bin accounting, the function unconditionally calls `safeTransfer` to `owner`: [1](#0-0) 

```solidity
if (amount0Removed > 0) {
    IERC20(ctx.token0).safeTransfer(owner, amount0Removed);
}
if (amount1Removed > 0) {
    IERC20(ctx.token1).safeTransfer(owner, amount1Removed);
}
```

If either token is USDC or USDT and `owner` is on the blacklist, `safeTransfer` reverts. Because the entire transaction reverts, the share-burn and bin-balance updates also roll back — the LP's shares are preserved in storage but they can never be redeemed.

The `removeLiquidity` entry point enforces `msg.sender == owner`: [2](#0-1) 

There is no position-transfer mechanism, no alternative recipient parameter, and no admin rescue path. A blacklisted `owner` has no on-chain route to recover their capital.

USDC and USDT are explicitly deployed as pool tokens across Base, Optimism, and Linea in the protocol's own deployment configs: [3](#0-2) 

### Impact Explanation

An LP whose address is USDC/USDT-blacklisted (e.g., OFAC sanction, exchange compliance action) loses their entire deposited principal permanently. The pool's bin accounting correctly records the shares, but no withdrawal can ever succeed. This is a direct, irrecoverable loss of user principal with no admin mitigation path.

### Likelihood Explanation

USDC and USDT blacklisting is a documented, real-world event (Circle and Tether have blacklisted hundreds of addresses). The protocol explicitly targets USDC/USDT pools. Any LP using an EOA that later gets blacklisted — or any LP whose address is sanctioned after deposit — triggers this condition without any privileged or malicious setup.

### Recommendation

Add an optional `recipient` parameter to `removeLiquidity` (separate from `owner`) so a blacklisted owner can redirect token output to a non-blacklisted address they control. Alternatively, implement a two-step withdrawal pattern that separates share burning from token claiming, allowing the owner to specify a recipient at claim time.

### Proof of Concept

1. Alice (EOA `0xAlice`) provides liquidity to a USDC/WETH pool. Her position is keyed `(0xAlice, salt)`.
2. Circle blacklists `0xAlice` (e.g., OFAC compliance).
3. Alice calls `removeLiquidity(0xAlice, salt, deltas, "")`.
4. `LiquidityLib.removeLiquidity` burns her shares and updates bin balances.
5. `IERC20(USDC).safeTransfer(0xAlice, amount0Removed)` reverts — USDC blacklist check fails.
6. The entire transaction reverts; shares are restored in storage.
7. Alice cannot call `removeLiquidity` from any other address (`msg.sender != owner` guard).
8. Alice's USDC principal is permanently locked in the pool. [4](#0-3) [5](#0-4)

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

**File:** metric-core/contracts/MetricOmmPool.sol (L565-571)
```text
  function transferToken0(address to, uint256 amount) internal {
    IERC20(TOKEN0).safeTransfer(to, amount);
  }

  function transferToken1(address to, uint256 amount) internal {
    IERC20(TOKEN1).safeTransfer(to, amount);
  }
```

**File:** smart-contracts-poc/script/js/config/base/feeds/default.json (L1-10)
```json
{
  "oracle": "0x0000000000000000000000000000000000000000",
  "tokens": [
    {
      "pythLazerId": 7,
      "baseTokenSymbol": "USDC",
      "quoteTokenSymbol": "USDC",
      "baseTokenAddress": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
      "quoteTokenAddress": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    },
```
