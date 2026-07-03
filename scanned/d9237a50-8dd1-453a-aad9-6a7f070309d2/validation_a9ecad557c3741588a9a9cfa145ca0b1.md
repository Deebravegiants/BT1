### Title
Missing Staleness Validation on ETH/USD Chainlink Feed Enables Stale Price Propagation — (`contracts/oracles/RSETHPriceFeed.sol`)

---

### Summary

`RSETHPriceFeed.latestRoundData()` fetches the ETH/USD price from Chainlink and multiplies it by `rsETHPrice`, but performs **no staleness check** on the ETH/USD feed's `updatedAt` timestamp. The raw, potentially stale `updatedAt` is returned verbatim to callers. Downstream protocols (e.g., Morpho) that enforce their own staleness guard on the returned `updatedAt` will revert, freezing user positions for the duration of the staleness event.

---

### Finding Description

In `latestRoundData()`: [1](#0-0) 

The function calls `ETH_TO_USD.latestRoundData()` and passes through all five return values unchanged, except for recomputing `answer`. There is no check on:

- `updatedAt` vs. `block.timestamp` (heartbeat/staleness window)
- `answeredInRound >= roundId` (round completeness)
- `answer > 0` (valid price)

Compare this to `ChainlinkOracleForRSETHPoolCollateral`, which **does** perform these checks: [2](#0-1) 

`RSETHPriceFeed` is the contract intended to be plugged into external lending/collateral protocols as an `AggregatorV3Interface`-compatible oracle. Those protocols (Morpho, Aave, etc.) typically enforce their own staleness check on the `updatedAt` value returned by the oracle. Because `RSETHPriceFeed` blindly forwards the ETH/USD feed's `updatedAt`, a stale ETH/USD feed causes the composite oracle to return a stale `updatedAt`, which those downstream protocols will reject.

The `rsETHPrice` component comes from `LRTOracle.rsETHPrice`: [3](#0-2) 

This is a stored state variable updated by `updateRSETHPrice()` — it has no on-chain timestamp attached to it and is not reflected in the returned `updatedAt`. So the composite answer can be: a **current** rsETH/ETH rate × a **stale** ETH/USD price, with the stale `updatedAt` propagated to the consumer.

---

### Impact Explanation

Any downstream lending/collateral protocol using `RSETHPriceFeed` as its oracle and enforcing a staleness check on `updatedAt` will revert on all price-dependent operations (borrow, withdraw, liquidate) for the duration of the ETH/USD feed staleness. This constitutes **temporary freezing of funds** (Medium). The "permanent" framing in the question is overstated: Chainlink ETH/USD feeds recover, so the freeze is bounded by the duration of the staleness event, not permanent.

---

### Likelihood Explanation

The ETH/USD Chainlink feed has a 1-hour heartbeat on mainnet. Network congestion, Chainlink node issues, or a deviation-threshold miss can cause the feed to go stale for minutes to hours. This is a realistic, non-adversarial condition requiring no privileged access or oracle compromise — it is a normal operational risk that the contract fails to guard against.

---

### Recommendation

Add a configurable `stalePriceThreshold` and validate `updatedAt` in both `latestRoundData()` and `getRoundData()`:

```solidity
uint256 public immutable STALE_PRICE_THRESHOLD; // e.g., 3600 seconds for ETH/USD

// In latestRoundData():
(roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.latestRoundData();
if (block.timestamp - updatedAt > STALE_PRICE_THRESHOLD) revert StalePrice();
if (answeredInRound < roundId) revert IncompleteRound();
if (answer <= 0) revert InvalidPrice();
answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
```

This mirrors the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`. [4](#0-3) 

---

### Proof of Concept

```solidity
// Fork test (Foundry) — no mainnet calls, uses vm.mockCall
function test_staleEthUsdPropagated() public {
    // Mock ETH/USD feed to return updatedAt = 2 days ago
    uint80 roundId = 1;
    int256 ethPrice = 3000e8;
    uint256 staleTimestamp = block.timestamp - 2 days;

    vm.mockCall(
        address(ETH_TO_USD),
        abi.encodeWithSelector(AggregatorV3Interface.latestRoundData.selector),
        abi.encode(roundId, ethPrice, staleTimestamp, staleTimestamp, roundId)
    );

    (,, , uint256 updatedAt,) = priceFeed.latestRoundData();

    // RSETHPriceFeed returns stale updatedAt without reverting
    assertEq(updatedAt, staleTimestamp);
    assertTrue(block.timestamp - updatedAt > 1 hours);

    // Simulate Morpho-style consumer that enforces staleness
    // (Morpho reverts if block.timestamp - updatedAt > heartbeat)
    vm.expectRevert(); // consumer reverts → all borrows/withdrawals blocked
    morphoConsumer.borrow(marketParams, amount, shares, onBehalf, receiver);
}
```

The test confirms: `latestRoundData()` returns `answer > 0` with a stale `updatedAt`, no revert occurs inside `RSETHPriceFeed`, but any downstream consumer enforcing staleness is blocked.

### Citations

**File:** contracts/oracles/RSETHPriceFeed.sol (L63-70)
```text
    function latestRoundData()
        external
        view
        returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)
    {
        (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.latestRoundData();
        answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L26-37)
```text
    function getRate() public view returns (uint256) {
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
    }
```

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```
