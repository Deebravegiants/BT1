### Title
Single Asset Oracle Failure Permanently Blocks rsETH Price Updates for All Assets — (`contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle._getTotalEthInProtocol()` iterates over every supported asset and calls `getAssetPrice(asset)` for each one inside a single loop. If any one asset's price oracle permanently reverts (e.g., a Chainlink feed goes stale/offline, or an underlying LST protocol fails), the entire `updateRSETHPrice()` call reverts. The stored `rsETHPrice` then becomes permanently stale, the downside-protection auto-pause mechanism can never trigger, fee minting is permanently blocked, and — critically — if a slashing event occurs while the price is frozen, users can drain the protocol by withdrawing at the inflated stored price.

---

### Finding Description

`LRTOracle._getTotalEthInProtocol()` aggregates the ETH value of all supported assets:

```solidity
for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
    address asset = supportedAssets[assetIdx];
    uint256 assetER = getAssetPrice(asset);          // ← reverts if oracle fails
    uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
    totalETHInProtocol += totalAssetAmt.mulWad(assetER);
    unchecked { ++assetIdx; }
}
``` [1](#0-0) 

`getAssetPrice(asset)` delegates to the registered `IPriceFetcher` (e.g., `ChainlinkPriceOracle`, `RETHPriceOracle`, `EthXPriceOracle`). Each of these makes a live external call to the underlying protocol or Chainlink feed: [2](#0-1) [3](#0-2) [4](#0-3) 

If any one of these external calls reverts — due to a Chainlink feed going offline, an LST protocol pausing its rate function, or any other failure — `_getTotalEthInProtocol()` reverts, which causes `_updateRsETHPrice()` to revert: [5](#0-4) 

The stored `rsETHPrice` is then permanently frozen at its last value. The downside-protection block inside `_updateRsETHPrice()` — which auto-pauses the deposit pool and withdrawal manager when the price drops too far — can never execute: [6](#0-5) 

The `unlockQueue` function in `LRTWithdrawalManager` uses the **stored** `rsETHPrice` (not a live call) to calculate how much asset to disburse to users: [7](#0-6) [8](#0-7) 

If the true rsETH price has dropped (e.g., due to EigenLayer slashing) but the stored price is frozen at a higher value, operators can still call `unlockQueue` and users can claim assets at the inflated rate, draining the protocol.

---

### Impact Explanation

**Permanent freezing of unclaimed yield**: Fee minting via `_checkAndUpdateDailyFeeMintLimit` inside `_updateRsETHPrice()` is permanently blocked. [9](#0-8) 

**Protocol insolvency**: If a slashing event causes the true rsETH value to drop while the stored `rsETHPrice` is frozen at a higher value, the auto-pause mechanism cannot trigger. Users can call `unlockQueue` and `completeWithdrawal` using the inflated stored price, receiving more assets than their rsETH is worth, draining the protocol at the expense of remaining depositors. [10](#0-9) 

---

### Likelihood Explanation

The protocol supports multiple LSTs (stETH, rETH, ETHx, sfrxETH, swETH) each with its own price oracle. The protocol is explicitly designed to be permissionless and integrate with external price feeds. A Chainlink feed going offline, an LST protocol pausing its exchange-rate function, or any other oracle-level failure for even one asset is a realistic scenario. The contest README explicitly acknowledges Chainlink integration risks. With `n` supported assets there are `n` independent failure points, any one of which triggers this condition.

---

### Recommendation

Wrap each `getAssetPrice(asset)` call inside `_getTotalEthInProtocol()` in a `try/catch` block. If a single oracle reverts, either skip that asset (with an emitted warning) or revert only if a configurable threshold of oracles fail. This mirrors the standard pattern for multi-asset aggregators and prevents a single oracle failure from freezing the entire price-update mechanism.

---

### Proof of Concept

1. Protocol supports assets: stETH, rETH, ETHx.
2. Alice deposits stETH and rETH, receiving rsETH. Both assets are staked in EigenLayer.
3. The Chainlink feed for rETH goes permanently offline (feed contract stops responding).
4. Anyone calls `updateRSETHPrice()`. Inside `_getTotalEthInProtocol()`, the loop reaches rETH and calls `getAssetPrice(rETH)` → `ChainlinkPriceOracle.getAssetPrice(rETH)` → `priceFeed.latestRoundData()` → **reverts**.
5. `updateRSETHPrice()` permanently reverts. `rsETHPrice` is frozen.
6. An EigenLayer slashing event reduces the true rsETH value from 1.05 ETH to 0.95 ETH.
7. The auto-pause mechanism inside `_updateRsETHPrice()` can never trigger because step 4 always reverts first.
8. An operator calls `unlockQueue(stETH, ...)`. It reads the frozen `rsETHPrice = 1.05 ETH` and the live stETH price. Users receive stETH calculated at the inflated 1.05 rate instead of the true 0.95 rate.
9. All rsETH holders who withdraw receive ~10.5% more stETH than they are entitled to, draining the protocol at the expense of remaining depositors.

### Citations

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
```

**File:** contracts/LRTOracle.sol (L231-232)
```text
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

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

**File:** contracts/LRTOracle.sol (L299-311)
```text
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
            }
        } else {
            _checkAndUpdateDailyFeeMintLimit(0);
        }
```

**File:** contracts/LRTOracle.sol (L336-348)
```text
        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

            unchecked {
                ++assetIdx;
            }
        }
```

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/oracles/RETHPriceOracle.sol (L34-40)
```text
    function getAssetPrice(address asset) external view returns (uint256) {
        if (asset != rETHAddress) {
            revert InvalidAsset();
        }

        return IrETH(rETHAddress).getExchangeRate();
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L824-834)
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
```

**File:** contracts/LRTWithdrawalManager.sol (L846-851)
```text
        return UnlockParams({
            rsETHPrice: lrtOracle.rsETHPrice(),
            assetPrice: lrtOracle.getAssetPrice(asset),
            totalAvailableAssets: unstakingVault.balanceOf(asset)
        });
    }
```
