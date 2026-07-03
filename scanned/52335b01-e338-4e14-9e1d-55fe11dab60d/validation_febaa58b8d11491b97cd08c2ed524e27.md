### Title
`SfrxETHPriceOracle` Assumes frxETH Pegs 1:1 to ETH, Causing Incorrect rsETH Pricing When frxETH Depegs — (`contracts/oracles/SfrxETHPriceOracle.sol`)

---

### Summary

`SfrxETHPriceOracle.getAssetPrice()` returns `ISfrxETH.pricePerShare()`, which yields the **sfrxETH/frxETH** exchange rate — not the **sfrxETH/ETH** rate. The oracle silently assumes frxETH ≡ 1 ETH. When frxETH trades below parity, the oracle overvalues sfrxETH, inflating `rsETHPrice` and enabling depositors to extract more rsETH than the actual ETH backing warrants, causing protocol insolvency.

---

### Finding Description

`SfrxETHPriceOracle` is registered in `LRTOracle.assetPriceOracle` for the sfrxETH asset. Its sole pricing logic is:

```solidity
// contracts/oracles/SfrxETHPriceOracle.sol
function getAssetPrice(address asset) external view returns (uint256) {
    if (asset != sfrxETHContractAddress) {
        revert InvalidAsset();
    }
    return ISfrxETH(sfrxETHContractAddress).pricePerShare();
}
``` [1](#0-0) 

The interface documents what `pricePerShare()` actually measures:

```solidity
interface ISfrxETH {
    /// @notice How much frxETH is 1E18 sfrxETH worth. Price is in ETH, not USD
    function pricePerShare() external view returns (uint256);
}
``` [2](#0-1) 

`pricePerShare()` is the **sfrxETH → frxETH** conversion rate (an ERC-4626 vault share price denominated in its underlying, frxETH). The comment "Price is in ETH" reflects the Frax team's assumption that frxETH ≡ 1 ETH — it does **not** mean the function queries an ETH market price. The true sfrxETH/ETH rate requires a second multiplication by the frxETH/ETH market rate, which is never performed.

This value feeds directly into `LRTOracle._getTotalEthInProtocol()`:

```solidity
uint256 assetER = getAssetPrice(asset);          // sfrxETH/frxETH, not sfrxETH/ETH
uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
``` [3](#0-2) 

And then into `rsETHPrice` computation:

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
``` [4](#0-3) 

And into rsETH minting in `LRTDepositPool.getRsETHAmountToMint()`:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [5](#0-4) 

---

### Impact Explanation

**Critical — Protocol Insolvency.**

Suppose frxETH trades at 0.95 ETH (a realistic depeg scenario) and sfrxETH has accrued 5% staking rewards, so `pricePerShare()` returns `1.05e18`. The oracle reports sfrxETH = 1.05 ETH, but the true market value is `1.05 × 0.95 = 0.9975 ETH`.

- `_getTotalEthInProtocol()` is inflated by ~5.3%.
- `rsETHPrice` is inflated proportionally.
- A new depositor sending sfrxETH receives fewer rsETH than they should (they pay the inflated price).
- Existing rsETH holders' redemption value is backed by fewer real ETH than the price implies.
- Any arbitrageur who deposits sfrxETH at the inflated oracle rate and redeems rsETH for ETH-denominated assets extracts value from the protocol, draining backing.

The insolvency compounds with every `updateRSETHPrice()` call while frxETH remains depegged.

---

### Likelihood Explanation

**Medium.** frxETH has historically maintained a tighter peg than stETH, but it is not immune to market stress. frxETH has traded below 0.99 ETH during periods of Curve pool imbalance and broader DeFi stress. The Curve frxETH/ETH pool is the primary liquidity venue; large redemptions or protocol-level events can push frxETH below parity. The vulnerability is always latent and activates automatically whenever frxETH depegs — no attacker action is required beyond depositing sfrxETH during a depeg event.

---

### Recommendation

Replace the single `pricePerShare()` call with a two-step calculation:

1. Obtain the sfrxETH/frxETH rate from `pricePerShare()`.
2. Obtain the frxETH/ETH market rate from a Chainlink `frxETH/ETH` feed (or Curve TWAP).
3. Return `pricePerShare() * frxETHToETHRate / 1e18`.

This mirrors how the analogous `SfrxEth` derivative in the Asymmetry protocol was recommended to be fixed: use the actual swap output from the Curve pool to determine the true ETH value.

---

### Proof of Concept

```
Precondition: frxETH/ETH market rate = 0.95 (Curve pool imbalance)
              sfrxETH pricePerShare()  = 1.05e18 (5% staking rewards accrued)

Oracle reports: getAssetPrice(sfrxETH) = 1.05e18  (assumes frxETH = 1 ETH)
True ETH value: 1.05 * 0.95 = 0.9975e18

Protocol holds: 1000 sfrxETH
Oracle TVL:     1050 ETH   (inflated)
True TVL:       997.5 ETH

rsETH supply:   1000
rsETHPrice set: 1.05 ETH/rsETH  (inflated)

Attacker deposits 100 sfrxETH (true value: 99.75 ETH)
Oracle mints:   100 * 1.05e18 / 1.05e18 = 100 rsETH
True rsETH due: 100 * 0.9975e18 / 1.05e18 ≈ 95 rsETH

Attacker receives 5 excess rsETH backed by no real ETH → insolvency.
```

### Citations

**File:** contracts/oracles/SfrxETHPriceOracle.sol (L8-11)
```text
interface ISfrxETH {
    /// @notice How much frxETH is 1E18 sfrxETH worth. Price is in ETH, not USD
    function pricePerShare() external view returns (uint256);
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

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L336-344)
```text
        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

```

**File:** contracts/LRTDepositPool.sol (L520-520)
```text
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```
