Audit Report

## Title
Unvalidated Chainlink `latestRoundData()` Return Values Freeze Deposits and Withdrawal Initiation — (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

## Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` with no validation of the returned `price` (no staleness check, no zero/negative guard). If any supported asset's Chainlink feed reverts or returns a non-positive price, the revert propagates uncaught through `LRTOracle.getAssetPrice()` into `LRTDepositPool.depositAsset()`, `LRTDepositPool.depositETH()`, `LRTWithdrawalManager.initiateWithdrawal()`, and `LRTOracle.updateRSETHPrice()`, temporarily freezing user deposits and new withdrawal requests until the feed recovers or an admin manually replaces the oracle.

## Finding Description

**Root cause — `ChainlinkPriceOracle.getAssetPrice()` (L49–55):**

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

No check on `answeredInRound >= roundId`, `updatedAt != 0`, or `price > 0`. When `price < 0`, the explicit cast `uint256(price)` produces a value near `type(uint256).max`; the subsequent `* 1e18` multiplication overflows and reverts under Solidity 0.8 checked arithmetic. When the feed itself reverts on `latestRoundData()`, the revert propagates directly.

**No fallback in `LRTOracle.getAssetPrice()` (L156–158):**

```solidity
function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
    return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
}
```

No try-catch, no secondary oracle.

**User-reachable deposit path — `LRTDepositPool._beforeDeposit()` → `getRsETHAmountToMint()` (L520):**

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

Called unconditionally from `depositAsset()` and `depositETH()`, both of which are public and unpermissioned.

**User-reachable withdrawal initiation path — `LRTWithdrawalManager.initiateWithdrawal()` → `getExpectedAssetAmount()` (L593):**

```solidity
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

`initiateWithdrawal()` is public and unpermissioned; a feed failure blocks all new withdrawal requests for the affected asset.

**rsETH price update path — `LRTOracle._getTotalEthInProtocol()` (L339):**

```solidity
uint256 assetER = getAssetPrice(asset);
```

Called in a loop over all supported assets; a single feed failure blocks `updateRSETHPrice()` entirely.

## Impact Explanation

**Medium — Temporary freezing of funds.**

A Chainlink feed failure on any single supported asset (stETH, rETH, ETHx, sfrxETH, swETH, ETH) causes:
1. All `depositAsset()` / `depositETH()` calls to revert — users cannot deposit.
2. All `initiateWithdrawal()` calls for that asset to revert — users cannot queue new withdrawal requests.
3. `updateRSETHPrice()` to revert — the rsETH exchange rate stalls.

The freeze persists until the Chainlink feed recovers or an admin manually calls `updatePriceOracleFor()` to swap the oracle. No automatic fallback exists. Funds already in the protocol are not directly stolen, but access is blocked, satisfying the "temporary freezing of funds" impact class.

## Likelihood Explanation

Chainlink feeds can enter a non-positive or reverting state during documented, real-world events: feed deprecation/migration to a new aggregator address, extreme market conditions triggering Chainlink's min/max answer circuit-breaker (which clamps `answer` to the configured bound, potentially returning a stale or zero value), or a feed being sunset. The protocol supports five LST assets plus ETH, each backed by a separate Chainlink feed, multiplying the attack surface. No attacker action is required — the condition arises from normal Chainlink infrastructure behavior. Any user attempting a deposit or withdrawal initiation during such a period will trigger the revert.

## Recommendation

1. **Validate all `latestRoundData()` return values** in `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
(uint80 roundId, int256 price, , uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();
require(price > 0, "Invalid price");
require(updatedAt != 0, "Incomplete round");
require(answeredInRound >= roundId, "Stale price");
require(block.timestamp - updatedAt <= MAX_STALENESS, "Price too stale");
```

2. **Add a try-catch fallback** in `LRTOracle.getAssetPrice()` so that if the primary oracle reverts, a secondary source (e.g., a TWAP or protocol-internal rate) is consulted before propagating the revert.

3. **Guard `_getTotalEthInProtocol()`** with per-asset try-catch so a single oracle failure does not block the entire rsETH price update.

## Proof of Concept

1. A supported asset's Chainlink feed (e.g., stETH/ETH) is deprecated and `latestRoundData()` begins reverting.
2. Any user calls `depositAsset(stETH, amount, 0, "")`.
3. Call chain: `depositAsset` → `_beforeDeposit` → `getRsETHAmountToMint` → `lrtOracle.getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` → `priceFeed.latestRoundData()` **reverts**.
4. The revert propagates with no try-catch at any layer; the deposit fails.
5. Simultaneously, any user calling `initiateWithdrawal(stETH, rsETHAmount, "")` hits the same path via `getExpectedAssetAmount` → `lrtOracle.getAssetPrice(stETH)` and also reverts.
6. `updateRSETHPrice()` reverts for the same reason, stalling protocol accounting.
7. No fallback oracle is consulted at any point.

**Foundry fork test sketch:**

```solidity
function test_staleOracleFreezeDeposit() public {
    // Deploy a mock feed that always reverts on latestRoundData()
    RevertingFeed feed = new RevertingFeed();
    // Admin swaps the stETH price feed to the reverting mock
    vm.prank(lrtManager);
    chainlinkOracle.updatePriceFeedFor(stETH, address(feed));
    // Any user deposit now reverts
    vm.prank(user);
    vm.expectRevert();
    lrtDepositPool.depositAsset(stETH, 1 ether, 0, "");
    // Any user withdrawal initiation also reverts
    vm.prank(user);
    vm.expectRevert();
    lrtWithdrawalManager.initiateWithdrawal(stETH, 1 ether, "");
}
```