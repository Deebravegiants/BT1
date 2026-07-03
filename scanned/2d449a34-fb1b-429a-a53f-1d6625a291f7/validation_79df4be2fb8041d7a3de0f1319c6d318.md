### Title
Protocol-Internal Rate Oracles for ethX and sfrxETH Allow Over-Valuation of TVL During LST De-Peg Events - (File: contracts/oracles/EthXPriceOracle.sol, contracts/oracles/SfrxETHPriceOracle.sol)

---

### Summary

`EthXPriceOracle` and `SfrxETHPriceOracle` return protocol-internal exchange rates rather than market prices. `LRTOracle._getTotalEthInProtocol()` uses these oracles to compute the protocol's total ETH value, which feeds directly into `rsETHPrice`. If ethX or sfrxETH de-pegs in the market while the protocol-internal rate remains unchanged, `rsETHPrice` is inflated relative to the real value of the underlying assets. Early rsETH holders who withdraw stETH (priced at market rate via Chainlink) receive more stETH than the protocol can sustainably pay, leaving later withdrawers unable to redeem their rsETH.

---

### Finding Description

`EthXPriceOracle.getAssetPrice()` delegates to `IETHXStakePoolsManager.getExchangeRate()`, which is the Stader protocol's internal accounting rate — not the market price of ethX: [1](#0-0) 

`SfrxETHPriceOracle.getAssetPrice()` delegates to `ISfrxETH.pricePerShare()`, which is the Frax protocol's internal share price — not the market price of sfrxETH: [2](#0-1) 

Both of these are consumed by `LRTOracle._getTotalEthInProtocol()`, which iterates over all supported assets and multiplies each asset's total deposited amount by its oracle price to compute the protocol's total ETH value: [3](#0-2) 

This total is then used to compute `rsETHPrice`: [4](#0-3) 

By contrast, stETH is priced via `ChainlinkPriceOracle`, which reads a live market feed: [5](#0-4) 

This creates an asymmetry: ethX and sfrxETH are valued at their protocol-internal rates (which do not fall during a market de-peg), while stETH is valued at its live market price. When a user withdraws stETH, the payout is:

```
underlyingToReceive = rsETHAmount * rsETHPrice / getAssetPrice(stETH)
``` [6](#0-5) 

If ethX de-pegs in the market but its protocol-internal rate is unchanged, `rsETHPrice` remains inflated relative to the real value of the protocol's assets. Users withdrawing stETH receive more stETH than the protocol can sustainably pay, draining stETH at the expense of later withdrawers.

---

### Impact Explanation

**Protocol insolvency (Critical).** If ethX or sfrxETH de-pegs significantly in the market while the protocol-internal rate remains unchanged:

1. `_getTotalEthInProtocol()` over-values the TVL.
2. `rsETHPrice` is inflated relative to the real value of the underlying assets.
3. Users who withdraw stETH (priced at market rate via Chainlink) receive more stETH than the protocol can afford.
4. The first withdrawers are paid in full; later withdrawers find the stETH pool drained and cannot redeem their rsETH.

This is a direct analog to the external report: the protocol uses a non-market price for a collateral token, leading to over-valuation and insolvency when the token de-pegs.

---

### Likelihood Explanation

**Low to Medium.** ethX and sfrxETH are established LSTs with deep liquidity. However, a significant de-peg is possible in scenarios such as a smart contract exploit in the Stader or Frax protocol, a regulatory action, or a market panic. The vulnerability is passive — no special attacker action is required beyond submitting a withdrawal request for stETH after the de-peg occurs.

---

### Recommendation

Replace protocol-internal rate oracles with market-price oracles (e.g., Chainlink feeds) for ethX and sfrxETH, consistent with how stETH is priced. Alternatively, use the minimum of the protocol-internal rate and the market price to ensure the protocol never over-values its collateral.

---

### Proof of Concept

1. Protocol holds 1000 ethX (protocol rate: 1.05 ETH/ethX = 1050 ETH) and 1000 stETH (market price: 1.0 ETH/stETH = 1000 ETH). Total TVL = 2050 ETH. rsETH supply = 2000. `rsETHPrice` = 1.025 ETH/rsETH.
2. ethX de-pegs: market price drops to 0.7 ETH/ethX. Real TVL = 700 + 1000 = 1700 ETH. But `EthXPriceOracle.getAssetPrice()` still returns 1.05, so `_getTotalEthInProtocol()` still returns 2050 ETH. `rsETHPrice` remains 1.025.
3. An rsETH holder calls `initiateWithdrawal` for stETH. `expectedAssetAmount = rsETHAmount * 1.025 / 1.0` — inflated.
4. The user claims the withdrawal and receives more stETH than the protocol can sustainably pay.
5. After enough such withdrawals, the stETH pool is drained. Later rsETH holders cannot redeem their tokens, resulting in permanent loss of funds. [7](#0-6) [1](#0-0) [2](#0-1) [8](#0-7)

### Citations

**File:** contracts/oracles/EthXPriceOracle.sol (L46-52)
```text
    function getAssetPrice(address asset) external view returns (uint256) {
        if (asset != ethxAddress) {
            revert InvalidAsset();
        }

        return IETHXStakePoolsManager(ethXStakePoolsManagerProxyAddress).getExchangeRate();
    }
```

**File:** contracts/oracles/SfrxETHPriceOracle.sol (L35-41)
```text
    function getAssetPrice(address asset) external view returns (uint256) {
        if (asset != sfrxETHContractAddress) {
            revert InvalidAsset();
        }

        return ISfrxETH(sfrxETHContractAddress).pricePerShare();
    }
```

**File:** contracts/LRTOracle.sol (L249-251)
```text
        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

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

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L580-594)
```text
    function getExpectedAssetAmount(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 underlyingToReceive)
    {
        // setup oracle contract
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```
