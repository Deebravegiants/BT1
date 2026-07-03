### Title
`SfrxETHPriceOracle` Incorrectly Assumes 1 frxETH == 1 ETH When Computing sfrxETH Price - (File: `contracts/oracles/SfrxETHPriceOracle.sol`)

### Summary

`SfrxETHPriceOracle.getAssetPrice()` returns `sfrxETH.pricePerShare()`, which gives **frxETH per sfrxETH**, not **ETH per sfrxETH**. The protocol silently treats frxETH as equivalent to ETH (1:1), mirroring the exact root cause of H-8: an incorrect token-equivalence assumption in an oracle rate computation.

### Finding Description

`SfrxETHPriceOracle` calls `ISfrxETH.pricePerShare()` and returns the result directly as the ETH price of sfrxETH: [1](#0-0) [2](#0-1) 

The interface comment itself states the return value is denominated in **frxETH**, not ETH:

```
/// @notice How much frxETH is 1E18 sfrxETH worth. Price is in ETH, not USD
```

The second clause ("Price is in ETH") is incorrect — sfrxETH is an ERC-4626 vault whose underlying asset is **frxETH**, a synthetic ETH derivative. `pricePerShare()` returns frxETH-per-sfrxETH. The protocol then uses this value as if it were ETH-per-sfrxETH, implicitly assuming 1 frxETH ≡ 1 ETH.

This price flows directly into `LRTOracle._getTotalEthInProtocol()`: [3](#0-2) 

which is consumed by `_updateRsETHPrice()` to compute the rsETH/ETH exchange rate: [4](#0-3) 

And `getRsETHAmountToMint` in `LRTDepositPool` uses both `getAssetPrice` and `rsETHPrice()` to determine how many rsETH tokens to mint per deposit: [5](#0-4) 

### Impact Explanation

When frxETH depegs below ETH (e.g., 1 frxETH = 0.95 ETH, which has occurred historically during Curve pool imbalances):

- `getAssetPrice(sfrxETH)` returns a value ~5% higher than the true ETH value of sfrxETH.
- `_getTotalEthInProtocol()` overestimates the protocol's ETH-denominated TVL.
- `rsETHPrice` is inflated.
- Users who hold rsETH can redeem it for more ETH than the protocol actually backs, draining ETH from other depositors.
- This constitutes **protocol insolvency** and **theft of funds from non-sfrxETH depositors**.

**Impact: Critical — Protocol insolvency / direct theft of user funds.**

### Likelihood Explanation

frxETH is not natively ETH; it is a synthetic derivative that requires active Curve AMM liquidity and Frax protocol solvency to maintain its peg. Historical on-chain data shows frxETH has traded below 1 ETH during periods of Curve pool imbalance. Any depositor can trigger the vulnerable path by depositing sfrxETH when frxETH is depegged, then other users redeem rsETH for ETH at the inflated rate. No privileged access is required.

### Recommendation

Compose the frxETH-per-sfrxETH rate from `pricePerShare()` with a frxETH/ETH market price (e.g., from a Chainlink frxETH/ETH feed or a Curve TWAP):

```solidity
// ETH per sfrxETH = (frxETH per sfrxETH) * (ETH per frxETH)
uint256 frxEthPerSfrxEth = ISfrxETH(sfrxETHContractAddress).pricePerShare();
uint256 ethPerFrxEth = IFrxEthOracle(frxEthOracle).getRate(); // e.g. Chainlink frxETH/ETH
return frxEthPerSfrxEth * ethPerFrxEth / 1e18;
```

This is the direct analog of the Pendle mitigation: multiply the share-to-underlying rate by the underlying-to-ETH rate rather than assuming 1:1.

### Proof of Concept

1. frxETH depegs: 1 frxETH = 0.95 ETH (observable on-chain via Curve pool).
2. sfrxETH `pricePerShare()` = 1.05e18 (frxETH per sfrxETH, reflecting staking yield).
3. `SfrxETHPriceOracle.getAssetPrice(sfrxETH)` returns `1.05e18` — treated as ETH, but true ETH value is `1.05 * 0.95 = 0.9975 ETH`.
4. Protocol holds 1000 sfrxETH. `_getTotalEthInProtocol()` counts `1050 ETH` instead of `997.5 ETH` — a ~5.3% overcount.
5. rsETH price is inflated by ~5.3%.
6. An attacker who deposited ETH earlier redeems rsETH and receives ~5.3% more ETH than they deposited, draining funds from other depositors.

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

**File:** contracts/LRTOracle.sol (L230-250)
```text
        // get total ETH in the protocol (normalized to 1e18)
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

        // calculate previousTVL using rsethSupply multiplied by rsETHPrice
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);

        IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

        // determine if the protocol is active (not paused)
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;

        // only take fee if TVL increased and protocol is not paused
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

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

**File:** contracts/LRTDepositPool.sol (L506-521)
```text
    function getRsETHAmountToMint(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 rsethAmountToMint)
    {
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
