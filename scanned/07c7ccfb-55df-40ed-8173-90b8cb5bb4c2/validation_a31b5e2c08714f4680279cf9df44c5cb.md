### Title
`LRTOracle._getTotalEthInProtocol` Does Not Operate in a Fail-Safe Manner — Single Oracle Revert Permanently Freezes rsETH Price Updates - (File: contracts/LRTOracle.sol)

### Summary
`LRTOracle._getTotalEthInProtocol()` loops over every supported asset and makes an external call to each asset's price oracle. If any single oracle reverts, the entire `updateRSETHPrice()` call reverts, permanently freezing the rsETH price, blocking protocol fee minting, and disabling the price-drop auto-pause safety mechanism until an admin manually removes the broken oracle.

### Finding Description
`_getTotalEthInProtocol()` iterates over all supported assets and calls `getAssetPrice(asset)` for each one:

```solidity
// contracts/LRTOracle.sol L336-L348
for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
    address asset = supportedAssets[assetIdx];
    uint256 assetER = getAssetPrice(asset);          // external call
    uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
    totalETHInProtocol += totalAssetAmt.mulWad(assetER);
    unchecked { ++assetIdx; }
}
```

`getAssetPrice` delegates to a third-party oracle contract:

```solidity
// contracts/LRTOracle.sol L156-L158
function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
    return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
}
```

The supported oracle contracts include `ChainlinkPriceOracle` (which calls `priceFeed.latestRoundData()`), `RETHPriceOracle` (calls `IrETH.getExchangeRate()`), `SfrxETHPriceOracle` (calls `ISfrxETH.pricePerShare()`), and `SwETHPriceOracle` (calls `ISwETH.getRate()`). All of these are external third-party contracts beyond the protocol's control.

`_getTotalEthInProtocol()` is called exclusively by `_updateRsETHPrice()`, which is called by the public `updateRSETHPrice()` and the manager-gated `updateRSETHPriceAsManager()`. There is no try-catch or low-level call wrapping any of these external oracle calls.

### Impact Explanation
If any single supported asset's price oracle reverts — for example, a Chainlink feed is deprecated and starts reverting, an LST protocol pauses its rate function, or a feed returns a negative price causing a downstream revert — then:

1. **Protocol fee minting is permanently frozen** (`_updateRsETHPrice` cannot complete, so `IRSETH.mint(treasury, ...)` is never reached), matching **Medium: Permanent freezing of unclaimed yield**.
2. **The rsETH price is frozen at its last stored value**, meaning depositors receive incorrect rsETH amounts based on a stale rate.
3. **The price-drop auto-pause safety mechanism cannot trigger** (lines 277–281), removing a critical circuit-breaker.

The freeze persists until an admin calls `updatePriceOracleFor` to replace or zero-out the broken oracle — an entirely manual, reactive remediation with no on-chain time bound.

### Likelihood Explanation
The protocol supports multiple LST assets (stETH, rETH, sfrxETH, swETH, cbETH, etc.), each with its own external oracle. Chainlink feeds are periodically deprecated; LST protocols (Rocket Pool, Frax, Swell) have historically paused or upgraded their rate contracts. As more assets are added, the probability that at least one oracle reverts at any given time increases monotonically. This is a realistic, non-hypothetical failure mode.

### Recommendation
Wrap each external oracle call in a try-catch (or low-level `staticcall`) inside `_getTotalEthInProtocol()`. On failure, either skip the asset and emit an event, or revert with a specific error identifying the broken oracle so the caller can act. This mirrors the fix applied to `RootManager.propagate` in Connext PR 2430.

```solidity
try IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset) returns (uint256 price) {
    totalETHInProtocol += totalAssetAmt.mulWad(price);
} catch {
    emit AssetPriceOracleFailed(asset);
    // decide: skip or revert with named error
}
```

### Proof of Concept

1. Protocol supports assets `[stETH, rETH, sfrxETH]`, each with an external oracle.
2. Rocket Pool upgrades its contracts and the old `rETH.getExchangeRate()` begins reverting.
3. Any caller (including a keeper bot or any EOA) calls `LRTOracle.updateRSETHPrice()`.
4. Execution reaches `_getTotalEthInProtocol()` → `getAssetPrice(rETH)` → `RETHPriceOracle.getAssetPrice(rETH)` → `IrETH(rETHAddress).getExchangeRate()` → **reverts**.
5. The revert bubbles up through `_getTotalEthInProtocol` → `_updateRsETHPrice` → `updateRSETHPrice`, causing the entire transaction to revert.
6. `rsETHPrice` is never updated; protocol fee minting never occurs; the price-drop auto-pause never fires.
7. This state persists until an admin manually calls `updatePriceOracleFor(rETH, newOracle)`.

Relevant lines: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
```

**File:** contracts/LRTOracle.sol (L214-231)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }

        if (highestRsethPrice == 0) {
            highestRsethPrice = rsETHPrice;
        }

        uint256 previousPrice = rsETHPrice;

        // get total ETH in the protocol (normalized to 1e18)
        uint256 totalETHInProtocol = _getTotalEthInProtocol();
```

**File:** contracts/LRTOracle.sol (L298-311)
```text
        // mint protocol fee as rsETH if there's a fee to take
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

**File:** contracts/LRTOracle.sol (L331-349)
```text
    function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
        address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetCount = supportedAssets.length;

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
    }
```
