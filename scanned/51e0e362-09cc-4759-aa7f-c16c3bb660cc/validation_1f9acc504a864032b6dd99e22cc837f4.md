### Title
Missing Chainlink Price Feed Integrity Validation Allows Stale/Invalid Prices to Corrupt rsETH Rate - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` consumes Chainlink `latestRoundData()` output without verifying the price is positive, the round is complete, or the data is fresh. Because `LRTOracle.updateRSETHPrice()` is a public function callable by anyone, an unprivileged actor can trigger an rsETH price update at the exact moment a Chainlink feed is stale or returning an invalid answer, causing the protocol-wide rsETH exchange rate to be set incorrectly. The same codebase already implements all three required checks in `ChainlinkOracleForRSETHPoolCollateral.sol`, confirming the protocol is aware of the requirement but failed to apply it to the core oracle path.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` reads from Chainlink but discards every field except `price`:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L52-54
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

Three integrity checks are absent:

| Check | Missing in `ChainlinkPriceOracle` | Present in `ChainlinkOracleForRSETHPoolCollateral` |
|---|---|---|
| `price > 0` | No | `if (ethPrice <= 0) revert InvalidPrice();` |
| Round completeness (`answeredInRound >= roundId`) | No | `if (answeredInRound < roundID) revert StalePrice();` |
| Timestamp validity (`updatedAt != 0`) | No | `if (timestamp == 0) revert IncompleteRound();` |

This price is consumed by `LRTOracle.getAssetPrice()` → `_getTotalEthInProtocol()` → `_updateRsETHPrice()`, which computes the global `rsETHPrice` stored on-chain and used for all deposits and withdrawals.

`updateRSETHPrice()` has no access control:

```solidity
// contracts/LRTOracle.sol L87-89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

Any external caller can invoke it at any time.

---

### Impact Explanation

**Scenario A — Stale price (feed lagging behind a depeg or recovery):**
A Chainlink LST/ETH feed goes stale while the true price has dropped (e.g., LST depeg). An attacker calls `updateRSETHPrice()` while the feed still reports the pre-depeg high price. `_getTotalEthInProtocol()` returns an inflated ETH value, `newRsETHPrice` is set above its true value. New depositors receive fewer rsETH tokens than they are entitled to — their yield is stolen in favour of existing holders who can redeem at the inflated rate.

**Scenario B — `price = 0` (deprecated or broken feed):**
If a feed returns `answer = 0`, `uint256(0)` propagates through `_getTotalEthInProtocol()`, collapsing `totalETHInProtocol` to near zero. `newRsETHPrice` falls far below `highestRsethPrice`, triggering the downside protection branch:

```solidity
// contracts/LRTOracle.sol L277-281
if (isPriceDecreaseOffLimit) {
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;
}
```

This pauses deposits and withdrawals for all users — a temporary freeze of funds — until an admin manually unpauses.

**Scenario C — Negative `int256` price cast to `uint256`:**
A negative Chainlink answer (possible on deprecated feeds) is silently cast to an astronomically large `uint256`. `totalETHInProtocol` becomes enormous, `newRsETHPrice` is set to an astronomical value, and subsequent depositors receive effectively zero rsETH for their assets — direct theft of depositor principal.

---

### Likelihood Explanation

Chainlink feeds go stale during Ethereum network congestion, oracle node outages, or feed deprecation events — all historically observed conditions. The attacker's only required action is to call the public `updateRSETHPrice()` at the moment the feed is stale or invalid. No privileged access, no front-running of a specific transaction, and no capital is required. The window of opportunity exists for as long as the feed remains stale.

---

### Recommendation

Apply the same three integrity checks already present in `ChainlinkOracleForRSETHPoolCollateral.sol` to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (price <= 0) revert InvalidPrice();
    // Optional: add a heartbeat check, e.g. require(block.timestamp - updatedAt <= MAX_DELAY)

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

---

### Proof of Concept

1. A supported LST (e.g., stETH) Chainlink feed goes stale — `updatedAt` is hours old and `answeredInRound < roundId`, but the contract has no check.
2. Attacker calls `LRTOracle.updateRSETHPrice()` (public, no role required).
3. Execution path: `updateRSETHPrice()` → `_updateRsETHPrice()` → `_getTotalEthInProtocol()` → `LRTOracle.getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` → stale `price` returned without revert.
4. `totalETHInProtocol` is computed using the stale price; `newRsETHPrice` is set to an incorrect value and written to `rsETHPrice`.
5. All subsequent deposits via `LRTDepositPool.depositAsset()` / `depositETH()` use this corrupted rate to mint rsETH, shortchanging or over-rewarding depositors.

**Key references:**

- Missing checks: [1](#0-0) 
- Existing correct checks (same codebase): [2](#0-1) 
- Public entry point with no access control: [3](#0-2) 
- Price used to compute total ETH in protocol: [4](#0-3) 
- Downside protection pause triggered by deflated price: [5](#0-4)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
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

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L277-281)
```text
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
```

**File:** contracts/LRTOracle.sol (L336-343)
```text
        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```
