### Title
Oracle Update Sandwich Attack via Permissionless `updateBySignature` with No Deadline in `CompressedOracleV1` - (File: smart-contracts-poc/contracts/oracles/compressed/CompressedOracle.sol)

### Summary
`CompressedOracleV1.updateBySignature` is callable by anyone holding a valid creator signature and carries **no deadline**. A MEV searcher who obtains a signed price-update payload (e.g., from a public relayer API) can hold it indefinitely, then atomically bundle: (1) a front-run swap at the stale price, (2) the oracle update, and (3) a back-run swap at the new price — extracting value from LP providers in a single block.

### Finding Description

**Root cause — no deadline in `updateBySignature`:** [1](#0-0) 

The signed message commits only to `(chainid, oracleAddress, feedCreator, newSlotValue)`. There is no `deadline` field. The design comment confirms this is intentional: [2](#0-1) 

Because the signature never expires, a searcher who intercepts a signed update (from a public push-relayer, a mempool broadcast, or a monitoring API) can:
- **Delay** submission until the price delta is maximally profitable.
- **Bundle** the update between two opposing swaps in a single block.

**Pool reads oracle price at swap time with no averaging:** [3](#0-2) [4](#0-3) 

Every `swap()` call fetches a fresh oracle quote. There is no TWAP, no price-averaging, and no built-in sandwich guard in the core pool.

**`CompressedOracleV1.price()` is a view — readable by anyone without an in-swap context:** [5](#0-4) 

Unlike the Chainlink/Pyth oracle (which enforces `pool.inSwap() == msg.sender`), the `CompressedOracleV1` price is publicly readable at any time, letting a searcher pre-compute exact profit before committing.

**`PriceVelocityGuardExtension` is optional and incomplete:** [6](#0-5) 

This extension is not part of the core pool and is not enforced at deployment. Even when present, it only checks velocity between consecutive swaps — it does not block the front-run swap (which executes at the old price before the oracle update).

### Impact Explanation
LP providers suffer direct token loss. The sandwich extracts the full price-delta × swap-size from the pool's bin balances:

- Front-run swap: pool sells token0 at old (lower) price → LP loses token0 cheaply.
- Oracle update: mid price rises.
- Back-run swap: pool buys token0 at new (higher) price → LP overpays.

Net LP loss ≈ `Δprice × swapSize − 2 × spreadFee`. For a 1 % price jump on a $500 k swap with a 0.1 % spread, the LP loss is ≈ $4,000 per oracle update cycle — repeatable every update.

### Likelihood Explanation
- `updateBySignature` is **permissionless**: any address can submit a valid signed payload.
- Signed payloads are typically distributed via public relayer APIs or broadcast to the mempool, making them trivially observable.
- The attack is profitable whenever `Δprice > 2 × spreadFee`. Infrequent oracle updates (hours or days between pushes) produce larger deltas, increasing profitability.
- No on-chain guard prevents the bundle; block builders on EVM chains routinely support atomic sandwich bundles.

### Recommendation
1. **Add a `deadline` parameter to `updateBySignature`** — bind the signature to `keccak256(abi.encode(chainid, oracleAddress, feedCreator, deadline, newSlotValue))` and revert if `block.timestamp > deadline`. This prevents a searcher from holding a signed update for an opportunistic submission.
2. **Require `PriceVelocityGuardExtension` (or equivalent) for all production pools** backed by `CompressedOracleV1`, so rapid price jumps revert the back-run swap.
3. Consider a **commit-reveal** or **private mempool** submission path for oracle updates to prevent front-running of the update transaction itself.

### Proof of Concept

```
Setup:
  - Pool: token0/token1, oracle mid = 1000 (8-dec), spread = 5 bps
  - Oracle operator signs newSlotValue encoding mid = 1020 (+2%)
  - Signed payload is published to a public relayer API

Attack bundle (single block):
  Tx1 (front-run):
    pool.swap(zeroForOne=false, amountSpecified=+500_000 token1, ...)
    → pool sells 500 token0 at mid=1000; searcher pays 500_000 token1

  Tx2 (oracle update):
    CompressedOracleV1.updateBySignature(feedCreator, newSlotValue, sig)
    → oracle mid updated to 1020

  Tx3 (back-run):
    pool.swap(zeroForOne=true, amountSpecified=+500 token0, ...)
    → pool buys 500 token0 at mid=1020; searcher receives ≈510_000 token1

Searcher profit ≈ 510_000 − 500_000 − 2×(500_000×0.0005) = 9,500 token1
LP loss         ≈ 9,500 token1 extracted from bin balances
```

The `updateBySignature` call at Tx2 succeeds because the timestamp in `newSlotValue` is strictly newer than the stored slot timestamp, and the ECDSA signature is valid — no other guard exists. [7](#0-6)

### Citations

**File:** smart-contracts-poc/contracts/oracles/compressed/CompressedOracle.sol (L163-169)
```text
    function price(bytes32 feedId, address /* pool */)
        external
        view
        returns (uint256 mid, uint256 spread, uint16 spread1, uint256 refTime)
    {
        return _price(feedId);
    }
```

**File:** smart-contracts-poc/contracts/oracles/compressed/CompressedOracle.sol (L271-302)
```text
    function updateBySignature(address feedCreator, uint256 newSlotValue, bytes calldata signature)
        external
        override
        returns (bool)
    {
        require(feedCreator != address(0), InvalidNamespace());

        uint256 namespace;
        assembly ("memory-safe") {
            namespace := shl(96, feedCreator) // [creator:20][zeros:12]
        }

        uint8 slotId = uint8(newSlotValue); // LSB
        TimeMs timestampMs = toTimeMs(newSlotValue >> 8 & X56);
        timestampMs.revertIfAfterBlockTimeWithDrift(MAX_TIME_DRIFT);
        bytes32 key = bytes32(namespace | uint256(slotId));
        uint256 old = uint256(_loadStorage(key));
        TimeMs oldTimestampMs = toTimeMs(old >> 8 & X56);

        bool newer = timestampMs.isAfter(oldTimestampMs);
        if (!newer) {
            return false;
        }

        bytes32 hash = MessageHashUtils.toEthSignedMessageHash(
            keccak256(abi.encode(block.chainid, address(this), feedCreator, newSlotValue))
        );
        require(feedCreator == ECDSA.recover(hash, signature));

        _writeStorage(key, bytes32(newSlotValue & ~uint256(0xff)));

        return true;
```

**File:** smart-contracts-poc/contracts/oracles/compressed/docs/en/slot-structure.md (L64-66)
```markdown
There is **no deadline** on either push path: each word carries its own timestamp and
the per-slot monotonicity check neutralizes replay (a replayed word is "not newer" and
is skipped).
```

**File:** metric-core/contracts/MetricOmmPool.sol (L227-228)
```text
    uint256 packedSlot0Initial = Slot0Library.loadPackedSlot0();
    (uint128 bidPriceX64, uint128 askPriceX64) = _getBidAndAskPriceX64();
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

**File:** metric-periphery/contracts/extensions/PriceVelocityGuardExtension.sol (L36-79)
```text
  function beforeSwap(
    address,
    address,
    bool,
    int128,
    uint128,
    uint256,
    uint128 bidPriceX64,
    uint128 askPriceX64,
    bytes calldata
  ) external override returns (bytes4) {
    address pool_ = msg.sender;
    (uint256 midPriceX64,) = SwapMath.midAndSpreadFeeX64FromBidAsk(uint256(bidPriceX64), uint256(askPriceX64));
    // casting to `uint128` is safe: geometric mid of two uint128 bid/ask quotes fits uint128 (same bound as pool)
    // forge-lint: disable-next-line(unsafe-typecast)
    uint128 midPrice = uint128(midPriceX64);

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

    return IMetricOmmExtensions.beforeSwap.selector;
  }
```
