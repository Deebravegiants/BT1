Audit Report

## Title
Single Reverting Asset Price Oracle Permanently Blocks All rsETH Price Updates — (File: `contracts/LRTOracle.sol`)

## Summary
`LRTOracle._getTotalEthInProtocol()` iterates over every supported asset and calls `getAssetPrice(asset)` with no `try/catch` or skip logic. If any one asset's price oracle reverts — due to Chainlink sequencer downtime, a deprecated aggregator, or a stale-price circuit breaker — the entire `updateRSETHPrice()` call reverts. Protocol fee minting and the rsETH exchange rate update are both blocked until an admin manually replaces the broken oracle.

## Finding Description
`_getTotalEthInProtocol()` (lines 336–348) loops over all supported assets and calls `getAssetPrice(asset)` on each:

```solidity
// LRTOracle.sol L336–348
for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
    address asset = supportedAssets[assetIdx];
    uint256 assetER = getAssetPrice(asset);   // hard revert if oracle fails
    uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
    totalETHInProtocol += totalAssetAmt.mulWad(assetER);
    unchecked { ++assetIdx; }
}
```

`getAssetPrice` is guarded by `onlySupportedOracle` (lines 40–45), which reverts when `assetPriceOracle[asset] == address(0)`. Beyond that, `IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset)` (line 157) can itself revert — Chainlink's `latestRoundData` is documented to revert on L2 sequencer downtime and on deprecated aggregators.

There is no `try/catch`, no `continue`, and no fallback. A single failing oracle causes the entire loop — and therefore `_updateRsETHPrice()` — to revert. Both public entry points (`updateRSETHPrice()` at line 87 and `updateRSETHPriceAsManager()` at line 94) call `_updateRsETHPrice()`, so neither can succeed while the broken oracle is registered.

## Impact Explanation
**Medium — Permanent freezing of unclaimed yield.** Protocol fees are minted inside `_updateRsETHPrice()` at lines 299–308 via `IRSETH.mint(treasury, rsethAmountToMintAsProtocolFee)`. While the oracle is broken, no fee mint can execute; accrued yield is frozen until an admin manually calls `updatePriceOracleFor` to replace the broken oracle. The protocol has no self-recovery path.

**Low — Contract fails to deliver promised returns.** The stored `rsETHPrice` becomes stale. All depositors and withdrawers transact at an incorrect exchange rate for the duration of the outage.

## Likelihood Explanation
No attacker action is required. Chainlink feeds are known to revert under real-world infrastructure conditions: L2 sequencer restarts, deprecated aggregators, and stale-price circuit breakers. The protocol supports multiple LST assets (stETH, ETHx, etc.), each with its own oracle adapter. With N supported assets, the probability that at least one oracle is temporarily unavailable grows with N. `updateRSETHPrice()` is a public function callable by anyone, so the blocked state is immediately observable.

## Recommendation
Wrap the `getAssetPrice` call in a `try/catch` inside `_getTotalEthInProtocol()` so that a single failing oracle does not block the entire aggregation:

```solidity
for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
    address asset = supportedAssets[assetIdx];
    try this.getAssetPrice(asset) returns (uint256 assetER) {
        uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
        totalETHInProtocol += totalAssetAmt.mulWad(assetER);
    } catch {
        emit AssetOracleFailure(asset); // at minimum log the failure
    }
    unchecked { ++assetIdx; }
}
```

Alternatively, revert only when the failing asset has a non-negligible TVL contribution and skip it otherwise.

## Proof of Concept
1. Protocol has two supported assets: `stETH` (oracle healthy) and `ETHx` (Chainlink aggregator deprecated on L2 after sequencer restart — `latestRoundData` reverts).
2. Anyone calls `updateRSETHPrice()` (public, no access control).
3. `_getTotalEthInProtocol()` processes `stETH` successfully, then calls `getAssetPrice(ETHx)`.
4. The `ETHx` oracle reverts. The entire transaction reverts.
5. `rsETHPrice` is never updated. Protocol fees are never minted. The price-drop auto-pause cannot fire.
6. This persists until an admin calls `updatePriceOracleFor(ETHx, newOracle)`.

**Foundry fork test outline:**
```solidity
function test_oracleRevertBlocksPriceUpdate() public {
    // Deploy a mock oracle for ETHx that always reverts
    RevertingOracle revertOracle = new RevertingOracle();
    vm.prank(admin);
    lrtOracle.updatePriceOracleFor(ETHx, address(revertOracle));

    // Public call reverts — price update is fully blocked
    vm.expectRevert();
    lrtOracle.updateRSETHPrice();
}
```