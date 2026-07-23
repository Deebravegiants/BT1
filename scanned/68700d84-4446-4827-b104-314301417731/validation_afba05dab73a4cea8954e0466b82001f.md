### Title
Same-block oracle price update enables risk-free arbitrage against LP positions - (File: metric-core/contracts/MetricOmmPool.sol)

### Summary
`MetricOmmPool.swap()` fetches a fresh oracle price on every invocation with no per-block price caching. Because the underlying oracle (Chainlink Data Streams / Pyth) accepts permissionless price pushes, an attacker can execute two swaps in the same block at different prices — one at the stale on-chain price and one at the freshly pushed price — extracting value from LPs with zero directional risk.

### Finding Description

Every call to `swap()` immediately calls `_getBidAndAskPriceX64()`:

```solidity
// MetricOmmPool.sol:228
(uint128 bidPriceX64, uint128 askPriceX64) = _getBidAndAskPriceX64();
```

`_getBidAndAskPriceX64()` calls `IPriceProvider.getBidAndAskPrice()` live on every invocation with no block-level cache:

```solidity
// MetricOmmPool.sol:804-813
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

The price provider reads the oracle's stored data, which can be overwritten between two swap calls. For Chainlink Data Streams, `updateReport` is permissionless — any caller holding a valid DON-signed report can push it:

```solidity
// ChainlinkOracle.sol:68-70
function updateReport(bytes calldata fullReport) external {
    _store(_verifyReport(fullReport));
}
```

`_store` overwrites the stored price whenever the incoming report's timestamp is newer:

```solidity
// ChainlinkOracle.sol:91-94
if (d.timestampMs.isAfter(oracleData[feedId].timestampMs)) {
    oracleData[feedId] = d;
    emit ReportStored(feedId, d.price, d.spread0, d.timestampMs);
}
```

The pool's reentrancy guard (`nonReentrant(PoolActions.SWAP)`) and the `inSwap()` transient marker only prevent nested calls within a single swap execution. They impose no constraint on two sequential, independent `swap()` calls in the same transaction or block. There is no mechanism that locks the oracle price for the duration of a block.

### Impact Explanation

An attacker can atomically:
1. Swap at the stale on-chain price P₁ (buying token0 cheaply)
2. Push the newer signed oracle report with price P₂ > P₁
3. Swap in the opposite direction at P₂ (selling token0 at the higher price)

The attacker captures `(P₂ − P₁) × amount − fees` with zero directional risk. The loss is borne entirely by LPs whose deposited assets are sold at P₁ and repurchased at P₂. This directly reduces LP principal and constitutes a real token balance loss above Sherlock thresholds whenever the price delta exceeds the spread fee.

### Likelihood Explanation

Chainlink Data Streams and Pyth both publish signed price reports off-chain that anyone can push on-chain. A searcher monitoring the off-chain feed can observe a price move, hold the newer signed report, execute the first swap at the stale price, push the report, and execute the reverse swap — all within a single transaction. No privileged access is required. MEV infrastructure makes this straightforward on any chain where the protocol is deployed.

### Recommendation

Cache the oracle bid/ask at the first swap of each block and reuse it for all subsequent swaps in the same block. A transient-storage slot (EIP-1153, already used by the pool for the `inSwap` marker) is the natural fit:

```solidity
uint128 transient private _cachedBidX64;
uint128 transient private _cachedAskX64;

function _getBidAndAskPriceX64() internal returns (uint128, uint128) {
    if (_cachedBidX64 != 0) return (_cachedBidX64, _cachedAskX64);
    // ... existing fetch logic ...
    _cachedBidX64 = bid;
    _cachedAskX64 = ask;
    return (bid, ask);
}
```

Transient storage auto-clears at the end of each transaction, so the cache is naturally scoped to a single block's execution context and requires no manual cleanup.

### Proof of Concept

**Setup**: Pool with WBTC/USDC, spread fee = 1%. Off-chain Chainlink Data Streams has published two signed reports: R₁ (WBTC = $50,000, timestamp T) and R₂ (WBTC = $51,000, timestamp T+10). On-chain oracle currently holds R₁.

**Attack transaction** (single tx, block B):

1. Call `pool.swap(recipient, false, exactIn(50_000_USDC), MAX_PRICE)` → pool reads oracle → bid/ask derived from P₁=$50,000 → attacker receives ~1 WBTC for 50,000 USDC.
2. Call `oracle.updateReport(R₂)` → `_store` overwrites oracle data with P₂=$51,000 (newer timestamp accepted).
3. Call `pool.swap(recipient, true, exactIn(1_WBTC), 0)` → pool reads oracle → bid/ask derived from P₂=$51,000 → attacker receives ~51,000 USDC for 1 WBTC.

**Result**: Attacker nets ~$1,000 minus fees (~$1,010 spread fee at 1% on $50k + $51k ≈ $1,010). With a 2% price move and 1% spread, profit ≈ $500 per round trip. Larger positions or wider price moves scale the profit linearly. LPs absorb the loss. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L228-228)
```text
    (uint128 bidPriceX64, uint128 askPriceX64) = _getBidAndAskPriceX64();
```

**File:** metric-core/contracts/MetricOmmPool.sol (L485-490)
```text
  function inSwap() external view returns (address priceProvider_) {
    if (_currentAction() == PoolActions.SWAP) {
      return _resolvedPriceProvider();
    }
    return address(0);
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
