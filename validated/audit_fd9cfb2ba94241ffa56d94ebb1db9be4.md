Audit Report

## Title
Missing Staleness and Validity Checks on `latestRoundData()` Enables Stale Prices to Corrupt rsETH Minting and Withdrawal Accounting - (File: contracts/oracles/ChainlinkPriceOracle.sol)

## Summary

`ChainlinkPriceOracle.getAssetPrice()` calls Chainlink's `latestRoundData()` but discards all return values except `price`, performing no staleness, round-completeness, or sign validation. The same codebase already implements these checks in `ChainlinkOracleForRSETHPoolCollateral.getRate()`, confirming this is a code-level defect rather than an accepted design choice. A stale price propagates directly into rsETH minting, rsETH price updates, and withdrawal sizing, enabling protocol insolvency reachable by any unprivileged depositor or withdrawer.

## Finding Description

`ChainlinkPriceOracle.getAssetPrice()` at L49–55 of `contracts/oracles/ChainlinkPriceOracle.sol`:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

`roundId`, `startedAt`, `updatedAt`, and `answeredInRound` are all silently discarded. No guard exists for:
- `block.timestamp - updatedAt > TIMEOUT` (staleness)
- `answeredInRound < roundId` (incomplete round)
- `price <= 0` (invalid/negative price)
- `updatedAt == 0` (uninitialized round)

By contrast, `contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol` L26–37 in the same repository performs all three validity checks before returning a price, demonstrating the protocol is aware of the requirement and has implemented it selectively.

The unvalidated price feeds directly into three critical accounting paths:

1. **rsETH minting** (`contracts/LRTDepositPool.sol` L520): `rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice()`
2. **rsETH price update** (`contracts/LRTOracle.sol` L339–343): `uint256 assetER = getAssetPrice(asset); totalETHInProtocol += totalAssetAmt.mulWad(assetER)`
3. **Withdrawal sizing** (`contracts/LRTWithdrawalManager.sol` L593): `underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset)`

All three paths are reachable by any unprivileged external caller through public deposit and withdrawal functions.

## Impact Explanation

**Critical — Protocol insolvency.** If a Chainlink aggregator for any supported LST (stETH, ETHx, sfrxETH) freezes while the real market price has diverged:

- An inflated stale price causes `_getTotalEthInProtocol()` to overstate backing, `updateRSETHPrice()` to set `rsETHPrice` too high, and existing holders to redeem more LST than the protocol holds, draining collateral until insolvency.
- A deflated stale price causes new depositors to receive excess rsETH, diluting all existing holders and understating liabilities.

Both directions result in direct, concrete loss of user funds held in the protocol, satisfying the Critical impact class of "Protocol insolvency."

## Likelihood Explanation

Chainlink aggregators have historically paused during extreme market events (March 2020 ETH crash, LUNA collapse). Any one of the multiple supported LST feeds going stale is sufficient to trigger the vulnerability. No privileged access, no attacker capital, and no special conditions are required beyond the oracle feed lagging — any user calling `depositAsset()` or `initiateWithdrawal()` during a stale-price window triggers the mispricing. The vulnerability is repeatable for every transaction during the stale window.

## Recommendation

Apply the same validation pattern already present in `ChainlinkOracleForRSETHPoolCollateral.getRate()` to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
(uint80 roundId, int256 price, , uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();

if (answeredInRound < roundId) revert StalePrice();
if (updatedAt == 0) revert IncompleteRound();
if (price <= 0) revert InvalidPrice();
if (block.timestamp - updatedAt > STALENESS_TIMEOUT) revert StalePrice();
```

`STALENESS_TIMEOUT` should be configurable per asset feed, set to match each Chainlink feed's documented heartbeat interval.

## Proof of Concept

1. Deploy a fork of mainnet with the current `ChainlinkPriceOracle` contract.
2. Register stETH/ETH Chainlink feed for stETH as a supported asset.
3. Warp block timestamp forward by `heartbeat + 1` seconds without advancing the Chainlink aggregator round (simulating a frozen feed). The last reported price is `1.05e18`.
4. Separately record that the real stETH price has dropped to `0.90e18` (e.g., via a slashing event).
5. Call `LRTDepositPool.depositAsset(stETH, 100e18)` — `getAssetPrice(stETH)` returns `1.05e18` (stale).
6. Assert that `rsethAmountToMint` is computed using `1.05e18` instead of `0.90e18`, granting the depositor ~16.7% excess rsETH.
7. Call `LRTOracle.updateRSETHPrice()` — `rsETHPrice` is set using the stale `1.05e18` rate, inflating the price.
8. Call `LRTWithdrawalManager.initiateWithdrawal(stETH, rsethAmount)` — `getExpectedAssetAmount` returns more stETH than the deposited value warrants.
9. Assert that total rsETH liabilities now exceed the real ETH value of collateral, confirming insolvency.