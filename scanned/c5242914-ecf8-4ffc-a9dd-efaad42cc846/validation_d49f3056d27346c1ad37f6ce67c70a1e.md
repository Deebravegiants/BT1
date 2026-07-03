### Title
Chainlink `latestRoundData()` Return Values Not Validated — Stale or Invalid Price Accepted Without Checks - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards all return values except `answer`. No staleness check (`updatedAt`), no round-completeness check (`answeredInRound >= roundId`), and no non-negative check on `price` are performed. This is the direct analog of the Pyth confidence-interval omission: the oracle reliability signal exists in the data but is never consulted.

### Finding Description
In `contracts/oracles/ChainlinkPriceOracle.sol`, `getAssetPrice()` fetches the Chainlink price as follows:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

All five return values from `latestRoundData()` — `roundId`, `answer`, `startedAt`, `updatedAt`, `answeredInRound` — are available, but only `answer` is used. The contract never checks:

- `updatedAt == 0` or `updatedAt < block.timestamp - heartbeat` (stale price)
- `answeredInRound >= roundId` (incomplete round / stale round)
- `price > 0` (negative answer cast to `uint256` produces an astronomically large number)

By contrast, the sibling contract `ChainlinkOracleForRSETHPoolCollateral` performs all three of these checks:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
``` [2](#0-1) 

`ChainlinkPriceOracle` is the oracle registered for LST assets (stETH, rETH, swETH, etc.) in `LRTOracle`. Its output flows into two critical paths:

1. **Deposit minting** — `LRTDepositPool.getRsETHAmountToMint()` divides `lrtOracle.getAssetPrice(asset)` by `lrtOracle.rsETHPrice()` to determine how many rsETH tokens to mint for a depositor. [3](#0-2) 

2. **rsETH price update** — `LRTOracle._getTotalEthInProtocol()` multiplies each asset balance by `getAssetPrice(asset)` to compute total protocol TVL, which then sets `rsETHPrice`. [4](#0-3) 

### Impact Explanation
**Critical — Direct theft of user funds / protocol insolvency.**

If a Chainlink feed goes stale (e.g., sequencer outage, feed deprecation, extreme volatility causing circuit-breaker) while the last reported price is above the true market price, any depositor can call `depositAsset()` with the LST asset and receive rsETH computed at the inflated stale price. This mints excess rsETH backed by less real value, diluting all existing rsETH holders and causing protocol insolvency proportional to the price deviation and deposit size.

Conversely, if `price` is ever returned as a negative `int256` (possible during feed misconfiguration or a corrupted round), the unchecked cast `uint256(price)` produces a value near `2^256`, causing `_getTotalEthInProtocol()` to overflow or return a wildly incorrect TVL, corrupting `rsETHPrice` for all subsequent operations.

### Likelihood Explanation
Chainlink feeds do go stale: sequencer downtime on L2s, feed deprecation, and extreme volatility events are documented occurrences. The deposit path (`depositAsset`, `depositETH`) is permissionless and callable by any user at any time. No keeper or admin action is required to trigger the vulnerability — a depositor simply needs to observe that the feed is stale and act before it recovers.

### Recommendation
Apply the same validation pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();

if (answeredInRound < roundId) revert StalePrice();
if (updatedAt == 0 || block.timestamp - updatedAt > MAX_STALENESS) revert StalePrice();
if (price <= 0) revert InvalidPrice();
```

`MAX_STALENESS` should be set per-feed based on the Chainlink heartbeat (e.g., 3600 s for 1-hour feeds, 86 400 s for 24-hour feeds).

### Proof of Concept

1. Assume stETH/ETH Chainlink feed last updated 2 hours ago at 1.05 ETH; true market price has since dropped to 0.95 ETH (feed is stale, heartbeat exceeded).
2. Attacker calls `LRTDepositPool.depositAsset(stETH, 1000e18, 0, "")`.
3. `getRsETHAmountToMint` calls `ChainlinkPriceOracle.getAssetPrice(stETH)` → returns `1.05e18` (stale).
4. rsETH minted = `1000e18 * 1.05e18 / rsETHPrice`. At `rsETHPrice ≈ 1e18`, attacker receives `~1050` rsETH for 1000 stETH worth only `~950 ETH`.
5. Attacker redeems 1050 rsETH via withdrawal, extracting ~100 ETH of value from existing holders.
6. No admin action, no special role, no front-running required — only a stale feed and a `depositAsset` call. [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L30-32)
```text
        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTDepositPool.sol (L648-669)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```

**File:** contracts/LRTOracle.sol (L339-343)
```text
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```
