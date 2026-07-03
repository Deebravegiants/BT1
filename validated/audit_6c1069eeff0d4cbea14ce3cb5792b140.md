Audit Report

## Title
Missing Staleness Validation on Chainlink `latestRoundData()` Enables Stale-Price Minting Abuse - (File: contracts/oracles/ChainlinkPriceOracle.sol)

## Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards every return value except `answer`, with no check on `updatedAt`, `answeredInRound`, or price sign/zero. If a Chainlink feed goes stale, the last reported price is silently accepted and used to compute rsETH minting amounts. Because `rsETHPrice` is a separately stored value, a timing gap between the stale feed and the next price update allows an attacker to mint rsETH at an inflated rate, diluting existing holders.

## Finding Description
`ChainlinkPriceOracle.getAssetPrice()` at line 52 reads:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

All five return values of `latestRoundData()` — `roundId`, `answer`, `startedAt`, `updatedAt`, `answeredInRound` — are available per the interface declared at lines 14–17, but only `answer` is used. There is no check on `updatedAt` (staleness), `answeredInRound >= roundId` (round completeness), or `price > 0` (sign/zero validity). [2](#0-1) 

This price flows directly into `LRTDepositPool.getRsETHAmountToMint()`:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [3](#0-2) 

`rsETHPrice` is a stored state variable updated only when `updateRSETHPrice()` / `_updateRsETHPrice()` is explicitly called: [4](#0-3) 

This creates a timing gap: if a Chainlink feed goes stale at a price higher than the true market price, the numerator (`getAssetPrice(asset)`) reflects the inflated stale price while the denominator (`rsETHPrice`) still reflects the last correctly computed value. The minting ratio is therefore wrong in the attacker's favor.

The same stale price also flows into `_getTotalEthInProtocol()` via `getAssetPrice(asset)`: [5](#0-4) 

The `PriceAboveDailyThreshold` guard in `_updateRsETHPrice()` only triggers when `updateRSETHPrice()` is called — it does not block minting during the staleness window. [6](#0-5) 

The deposit limit (`depositLimitByAsset`) caps the scale of the attack but does not prevent it. [7](#0-6) 

## Impact Explanation
**Critical — Direct theft of user funds (existing rsETH holders).**

If a supported LST's Chainlink feed goes stale at a price higher than the true market price, an attacker deposits that LST and receives more rsETH than the deposited collateral is actually worth. The excess rsETH represents a dilution of all existing holders' pro-rata claims on the underlying TVL. When the attacker sells or redeems the rsETH, they extract real ETH value from the pool at the expense of honest holders. This matches the allowed impact: *Critical — Direct theft of any user funds*.

## Likelihood Explanation
Any unprivileged user can call `depositAsset()` or `depositETH()` — no special role is required. [8](#0-7) 

Chainlink feed staleness is realistic in several scenarios: L2 sequencer downtime (the protocol has L2 pool contracts such as `RSETHPoolV2`/`RSETHPoolV3` that rely on the same oracle infrastructure), feed deprecation, or network congestion delaying heartbeat updates. The attack window is the period between the feed going stale and the next `updateRSETHPrice()` call, which is not bounded on-chain.

## Recommendation
Add staleness and validity checks in `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
(uint80 roundId, int256 price, , uint256 updatedAt, uint80 answeredInRound)
    = priceFeed.latestRoundData();

require(price > 0, "Invalid price");
require(answeredInRound >= roundId, "Stale round");
require(updatedAt != 0, "Round not complete");
require(block.timestamp - updatedAt <= stalenessThreshold[asset], "Stale price");

return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

Store a per-feed configurable `stalenessThreshold` (heartbeat + buffer) alongside each feed address in `updatePriceFeedFor()`. For L2 deployments, additionally integrate a Chainlink L2 Sequencer Uptime Feed check before consuming any price data.

## Proof of Concept
1. Assume `cbETH/ETH` Chainlink feed last reported `1.05 ETH` per cbETH. The pool holds 100 cbETH; `rsETHPrice` was last computed as `1.05 ETH/rsETH` (100 rsETH outstanding, 105 ETH TVL).
2. The L2 sequencer goes offline; the feed stops updating. True market price of cbETH drops to `0.95 ETH`.
3. Attacker calls `depositAsset(cbETH, 100e18, 0, "")`.
4. `getRsETHAmountToMint` computes: `(100e18 × 1.05e18) / 1.05e18 = 100 rsETH` — using the stale numerator and the unchanged stored denominator.
5. Attacker receives 100 rsETH backed by only 95 ETH of true value. The pool now has 200 rsETH outstanding against 200 ETH true TVL (105 + 95), so each rsETH is worth 1.00 ETH instead of 1.05 ETH — a ~4.76% loss for all prior holders.
6. Attacker repeats until the per-asset deposit limit is exhausted or the oracle is corrected.

**Foundry fork test plan**: Fork an L2 (e.g., Arbitrum) at a block where a supported LST feed is live. Use `vm.mockCall` to freeze `latestRoundData()` at the current answer while advancing `block.timestamp` by more than the feed's heartbeat. Call `depositAsset()` as an unprivileged address and assert that `rsETHAmountToMint` exceeds the fair value computed with the true (post-drop) price, confirming the dilution of existing holders.

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L14-18)
```text
    function latestRoundData()
        external
        view
        returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound);
}
```

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L52-54)
```text
        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

**File:** contracts/LRTDepositPool.sol (L99-118)
```text
    function depositAsset(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedERC20Token(asset)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L520-520)
```text
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTDepositPool.sol (L661-662)
```text
        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
```

**File:** contracts/LRTOracle.sol (L252-265)
```text
        if (newRsETHPrice > highestRsethPrice) {
            // check if the price is above the threshold
            uint256 priceDifference = newRsETHPrice - highestRsethPrice;
            // pricePercentageLimit is in 1e18 precision (100% = 1e18, 1% = 1e16)
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

            // check if the price difference is above the threshold
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
```

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTOracle.sol (L339-343)
```text
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```
