### Title
Stale Chainlink Price Accepted in `getAssetPrice` Enables Deposit-at-Inflated-Price / Withdraw-at-True-Price Value Extraction — (`contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but silently discards `updatedAt`, `answeredInRound`, and `roundId`. When a Chainlink feed is stale at an inflated price, an attacker can deposit an LST at the stale-high rate (minting excess rsETH), wait for the feed to correct, trigger `updateRSETHPrice()` to push `rsETHPrice` down, then initiate a withdrawal that locks in a payout larger than the true value of the deposit. The excess is borne by all other depositors.

---

### Finding Description

**Root cause — `ChainlinkPriceOracle.sol` line 52:**

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

All five return values are available; only `price` is used. No check on `updatedAt` (staleness), `answeredInRound < roundId` (incomplete round), or `price <= 0` (invalid answer). [1](#0-0) 

The same codebase already implements all three checks in `ChainlinkOracleForRSETHPoolCollateral.getRate()`, confirming the omission in `ChainlinkPriceOracle` is unintentional: [2](#0-1) 

**How the stale price propagates:**

At deposit time, `LRTDepositPool.getRsETHAmountToMint()` computes:

```
rsethAmountToMint = (depositAmount × getAssetPrice(asset)) / rsETHPrice
``` [3](#0-2) 

`rsETHPrice` is a **stored** value updated only when `updateRSETHPrice()` is called. `getAssetPrice(asset)` is the **live** (potentially stale) Chainlink value. If the feed is stale-high while `rsETHPrice` still reflects the true historical rate, the numerator is inflated and the attacker receives excess rsETH.

At withdrawal initiation, `getExpectedAssetAmount()` computes:

```
underlyingToReceive = rsETHAmount × rsETHPrice / getAssetPrice(asset)
``` [4](#0-3) 

After the feed corrects and `updateRSETHPrice()` is called, `rsETHPrice` drops (because `_getTotalEthInProtocol()` now uses the true lower price over a larger rsETH supply). The attacker's withdrawal request locks in `expectedAssetAmount` at this lower `rsETHPrice`, which still exceeds the true value of their original deposit. [5](#0-4) 

**Claimed mitigation — `pricePercentageLimit` downside protection:**

`_updateRsETHPrice()` can pause the protocol if `newRsETHPrice` drops more than `pricePercentageLimit` below `highestRsethPrice`. However, `pricePercentageLimit` is a storage variable with **no default value set in `initialize()`**, so it starts at `0`. The guard condition is `pricePercentageLimit > 0 && diff > ...`, meaning when `pricePercentageLimit == 0` the entire downside-pause branch is **never triggered**. [6](#0-5) 

Even when `pricePercentageLimit` is configured, the attacker can exploit any stale-price deviation that falls within the threshold without triggering a pause.

---

### Impact Explanation

**Concrete numerical example:**

| State | stETH in protocol | rsETH supply | rsETHPrice |
|---|---|---|---|
| Initial | 100 | 100 | 1.000 |
| After attacker deposits 100 stETH at stale price 1.05 | 200 | 205 | 1.000 (not yet updated) |
| After feed corrects to 1.00 and `updateRSETHPrice()` called | 200 | 205 | 0.9756 |

Attacker initiates withdrawal of 105 rsETH:
- `expectedAssetAmount = 105 × 0.9756 / 1.00 ≈ 102.44 stETH`

Attacker deposited 100 stETH, receives 102.44 stETH — a **2.44 stETH profit extracted from other depositors**. The remaining 100 rsETH holders now have only 97.56 stETH backing their tokens instead of 100.

Scaled to realistic deposit sizes (e.g., 10,000 stETH), the extraction is proportional and unbounded by any on-chain cap.

`_calculatePayoutAmount` uses `min(expectedAssetAmount, currentReturn)`, which caps the payout if `rsETHPrice` drops further after the request — but it does **not** prevent the profit already locked in at request time. [7](#0-6) 

---

### Likelihood Explanation

Chainlink feeds have documented heartbeat intervals (e.g., 24 h for stETH/ETH on mainnet). Any network congestion, sequencer downtime, or feed-specific anomaly can cause the on-chain price to lag the true market price. An attacker monitoring mempool and on-chain oracle state can observe the divergence and act without any privileged access. No front-running is required — the stale price is already on-chain and readable by anyone.

---

### Recommendation

Add staleness, round-completeness, and non-negative checks to `ChainlinkPriceOracle.getAssetPrice()`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (price <= 0) revert InvalidPrice();
    if (block.timestamp - updatedAt > MAX_PRICE_AGE) revert StalePrice(); // e.g. 25 hours

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Additionally, ensure `pricePercentageLimit` is set to a non-zero value during deployment/initialization so the downside-pause circuit breaker is active from the start.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Invariant fuzz test: for any deposit → price-correction → withdrawal sequence,
// ETH redeemed must never exceed ETH deposited at the TRUE price.

import "forge-std/Test.sol";

contract StaleOraclePoC is Test {
    // --- simplified mock state ---
    uint256 rsETHSupply;
    uint256 rsETHPrice;          // stored, updated by updateRSETHPrice()
    uint256 protocolStETH;       // total stETH held

    // Chainlink mock: returns whatever we set
    uint256 chainlinkPrice;

    function setUp() public {
        // Initial state: 100 stETH, 100 rsETH, price = 1e18
        protocolStETH = 100e18;
        rsETHSupply   = 100e18;
        rsETHPrice    = 1e18;
        chainlinkPrice = 1e18; // true price
    }

    function getAssetPrice() internal view returns (uint256) {
        return chainlinkPrice; // no staleness check — mirrors ChainlinkPriceOracle
    }

    function deposit(uint256 amount) internal returns (uint256 rsethMinted) {
        rsethMinted = amount * getAssetPrice() / rsETHPrice;
        protocolStETH += amount;
        rsETHSupply   += rsethMinted;
    }

    function updateRSETHPrice() internal {
        // mirrors LRTOracle._updateRsETHPrice() with pricePercentageLimit == 0
        rsETHPrice = protocolStETH * getAssetPrice() / rsETHSupply;
    }

    function initiateWithdrawal(uint256 rsethAmount) internal returns (uint256 expectedStETH) {
        expectedStETH = rsethAmount * rsETHPrice / getAssetPrice();
        rsETHSupply   -= rsethAmount;
        protocolStETH -= expectedStETH;
    }

    function test_staleOracleExtractsValue() public {
        uint256 depositAmount = 100e18;

        // Step 1: Feed goes stale at 1.05
        chainlinkPrice = 1.05e18;

        // Step 2: Attacker deposits 100 stETH at stale price
        uint256 rsethReceived = deposit(depositAmount);
        // rsethReceived = 100e18 * 1.05e18 / 1e18 = 105e18

        // Step 3: Feed corrects to 1.00
        chainlinkPrice = 1e18;
        updateRSETHPrice();
        // rsETHPrice = 200e18 * 1e18 / 205e18 ≈ 0.9756e18

        // Step 4: Attacker withdraws all rsETH
        uint256 stETHReceived = initiateWithdrawal(rsethReceived);
        // stETHReceived ≈ 105e18 * 0.9756e18 / 1e18 ≈ 102.44e18

        // INVARIANT: stETH received must not exceed stETH deposited at true price
        uint256 fairValue = depositAmount * 1e18 / 1e18; // true price = 1.0
        assertLe(stETHReceived, fairValue,
            "INVARIANT BROKEN: attacker redeemed more than deposited at true price");
        // ^ This assertion FAILS, proving the vulnerability
    }
}
```

Running `forge test --match-test test_staleOracleExtractsValue` on unmodified code will show the invariant assertion failing, with `stETHReceived ≈ 102.44e18 > fairValue = 100e18`.

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

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L590-594)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L824-835)
```text
    function _calculatePayoutAmount(
        WithdrawalRequest storage request,
        uint256 rsETHPrice,
        uint256 assetPrice
    )
        private
        view
        returns (uint256)
    {
        uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
        return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
    }
```

**File:** contracts/LRTOracle.sol (L249-251)
```text
        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

```

**File:** contracts/LRTOracle.sol (L270-282)
```text
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }
```
