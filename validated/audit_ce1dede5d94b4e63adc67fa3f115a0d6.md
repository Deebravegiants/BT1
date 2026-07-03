Audit Report

## Title
Chainlink `minAnswer`/`maxAnswer` Circuit Breaker Not Validated in `ChainlinkPriceOracle.getAssetPrice()`, Enabling rsETH Over-Minting During LST Price Crash - (File: contracts/oracles/ChainlinkPriceOracle.sol)

## Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` and returns the raw price without checking whether it is clamped at the aggregator's `minAnswer` or `maxAnswer` circuit-breaker bounds. If a supported LST crashes in value, Chainlink's built-in circuit breaker returns `minAnswer` (a floor price higher than the real price), causing the protocol to mint rsETH against the crashed asset at the inflated floor price. This dilutes all existing rsETH holders and can render the protocol insolvent.

## Finding Description
`ChainlinkPriceOracle.getAssetPrice()` fetches the price from a Chainlink aggregator and discards all return values except `price`:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L49-55
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

It does not check `price` against the aggregator's `minAnswer`/`maxAnswer` bounds, does not check `answeredInRound >= roundId`, and does not check `updatedAt != 0`. Chainlink aggregators have a built-in circuit breaker: when the real market price falls below `minAnswer`, the aggregator continues to report `minAnswer` — the exact mechanism that caused the LUNA incident.

This price flows directly into `LRTOracle.getAssetPrice()`:

```solidity
// contracts/LRTOracle.sol L156-158
function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
    return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
}
```

Which feeds `_getTotalEthInProtocol()`:

```solidity
// contracts/LRTOracle.sol L336-343
uint256 assetER = getAssetPrice(asset);
uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```

And directly drives `getRsETHAmountToMint()`:

```solidity
// contracts/LRTDepositPool.sol L519-521
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

Called inside the public `depositAsset()` entry point:

```solidity
// contracts/LRTDepositPool.sol L99-118
function depositAsset(address asset, uint256 depositAmount, uint256 minRSETHAmountExpected, string calldata referralId)
    external nonReentrant whenNotPaused onlySupportedERC20Token(asset)
```

**Why existing guards are insufficient:**

The `pricePercentageLimit` downside-protection in `_updateRsETHPrice()` (L270–281) only triggers when `updateRSETHPrice()` is called. There is an exploitable window between the crash event and the next `updateRSETHPrice()` call during which `rsETHPrice` still reflects the pre-crash value. In this window, `depositAsset()` uses the live (clamped) Chainlink price for the numerator and the stale stored `rsETHPrice` for the denominator, maximizing the over-mint. Furthermore, if `pricePercentageLimit` is 0 (unset), there is no downside protection at all.

The same unchecked pattern exists in `ChainlinkOracleForRSETHPoolCollateral.getRate()` (L26–37), which checks `ethPrice <= 0` but not against `minAnswer`/`maxAnswer`.

## Impact Explanation
**Critical — Direct theft of existing rsETH holder funds / Protocol insolvency.**

Concrete example: stETH crashes from 1 ETH to 0.05 ETH; Chainlink clamps at `minAnswer = 0.5 ETH`. Protocol holds 500 stETH and 500 ETH of other assets; rsETH supply = 1000.

- Real TVL: `500 × 0.05 + 500 = 525 ETH`; real rsETHPrice = 0.525 ETH
- Reported TVL: `500 × 0.5 + 500 = 750 ETH`; stored rsETHPrice = 1.0 ETH (pre-crash, not yet updated)

Attacker deposits 1000 stETH (real value: 50 ETH):
- `getAssetPrice(stETH)` = 0.5 ETH (clamped, live)
- `rsETHPrice` = 1.0 ETH (stored, stale)
- rsETH minted = `1000 × 0.5 / 1.0 = 500 rsETH`

Real value of 500 rsETH at true price (0.525 ETH) ≈ 262 ETH. Attacker deposited 50 ETH of real value and received ~262 ETH of real value — a ~212 ETH theft from existing holders. When the price corrects, `rsETHPrice` drops and all existing rsETH holders are diluted by the phantom value minted.

This matches the allowed impact: **Critical — Direct theft of any user funds** and **Critical — Protocol insolvency**.

## Likelihood Explanation
**Medium.** Requires a significant, sudden LST price crash (analogous to LUNA/UST). While not a daily occurrence, the LST ecosystem has demonstrated such events are realistic. The attack requires no special permissions — any unprivileged user can call `depositAsset()` during the window when the circuit breaker is active and before `updateRSETHPrice()` is called. The window can be extended by front-running or simply acting quickly after the crash.

## Recommendation
After calling `latestRoundData()`, retrieve the aggregator's `minAnswer` and `maxAnswer` from the underlying `AggregatorInterface` and revert if the returned price is at or outside those bounds:

```solidity
interface IChainlinkAggregator {
    function minAnswer() external view returns (int192);
    function maxAnswer() external view returns (int192);
}

// In getAssetPrice():
IChainlinkAggregator aggregator = IChainlinkAggregator(priceFeed.aggregator());
int192 minAnswer = aggregator.minAnswer();
int192 maxAnswer = aggregator.maxAnswer();
if (price <= minAnswer || price >= maxAnswer) revert PriceOutOfBounds();
```

Also add staleness checks (`answeredInRound >= roundId` and `updatedAt != 0`) to `ChainlinkPriceOracle.getAssetPrice()`. Apply the same `minAnswer`/`maxAnswer` fix to `ChainlinkOracleForRSETHPoolCollateral.getRate()`.

## Proof of Concept
1. Deploy a mock Chainlink aggregator for stETH with `minAnswer = 0.5e18`.
2. Set stETH as a supported asset in the protocol with this feed.
3. Simulate a crash: configure the mock to return `price = 0.5e18` (the clamped floor) while the real market price is `0.05e18`.
4. Ensure `rsETHPrice` is stored at `1.0e18` (pre-crash, `updateRSETHPrice()` not yet called).
5. Call `LRTDepositPool.depositAsset(stETH, 1000e18, 0, "")` as an unprivileged attacker.
6. Observe: `getRsETHAmountToMint` computes `1000e18 × 0.5e18 / 1.0e18 = 500e18` rsETH minted.
7. Real value deposited: `1000 × 0.05 = 50 ETH`. rsETH received represents `500 × 1.0 = 500 ETH` of claimed value.
8. Call `updateRSETHPrice()` — price corrects downward, existing holders are diluted by the 450 ETH phantom value.

Foundry fork test: fork mainnet, mock the stETH/ETH Chainlink feed to return `minAnswer`, verify the rsETH minted exceeds the real ETH value deposited by the circuit-breaker ratio.