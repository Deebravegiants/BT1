### Title
Division by Zero in `getRsETHAmountToMint` When `rsETHPrice` Is Uninitialized or Zero Blocks All Mainnet Deposits — (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool.getRsETHAmountToMint()` divides by `lrtOracle.rsETHPrice()` without a zero guard. The `rsETHPrice` storage variable in `LRTOracle` is never set in `initialize()`, so it defaults to `0`. Any deposit call before `updateRSETHPrice()` is executed — or after a state where `totalETHInProtocol == 0` with non-zero rsETH supply and `pricePercentageLimit == 0` — causes an EVM division-by-zero revert, permanently blocking deposits until the price is refreshed.

### Finding Description
`LRTDepositPool.getRsETHAmountToMint()` performs the share-conversion calculation:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`lrtOracle.rsETHPrice()` is a plain `uint256` storage slot. `LRTOracle.initialize()` never writes to it, so it is `0` from deployment until `updateRSETHPrice()` is called. There is no zero-guard on the denominator before the division.

`_updateRsETHPrice()` handles the `rsethSupply == 0` case by setting `rsETHPrice = 1 ether` and returning early. However, if `rsethSupply > 0` and `totalETHInProtocol == 0` (all assets slashed/lost) **and** `pricePercentageLimit == 0` (the Solidity default — the downside-protection branch is skipped), the function computes `newRsETHPrice = 0 / rsethSupply = 0` and stores it, leaving `rsETHPrice = 0` for all subsequent callers.

The deposit entry points `depositETH()` and `depositAsset()` both call `_beforeDeposit()` → `getRsETHAmountToMint()`, so every deposit reverts under either condition.

By contrast, `viewSwapAssetToPremintedRsETH()` in `RSETHPoolV3ExternalBridge` **does** guard against a zero rate:
```solidity
if (rsETHToETHrate == 0) revert UnsupportedOracle();
```
confirming the protocol is aware of the zero-rate risk but did not apply the same guard to the deposit path.

### Impact Explanation
All user deposits via `LRTDepositPool.depositETH()` and `depositAsset()` revert with a division-by-zero panic. No rsETH can be minted. This constitutes a **temporary freezing of funds** (deposit functionality is completely unavailable) until `updateRSETHPrice()` is called and returns a non-zero price. Impact: **Medium — temporary freezing of funds**.

### Likelihood Explanation
Two realistic triggers exist:

1. **Deployment window:** `rsETHPrice` is `0` from contract deployment until `updateRSETHPrice()` is first called. Any deposit attempted in this window fails. `updateRSETHPrice()` is public but not called atomically with deployment.
2. **Total-loss state with default `pricePercentageLimit`:** If `pricePercentageLimit` is left at its default `0` (no admin action taken to set it), a scenario where all tracked ETH is drained (e.g., EigenLayer slashing, accounting bug) causes `_updateRsETHPrice()` to write `rsETHPrice = 0`, after which every deposit reverts until the price is manually refreshed.

### Recommendation
Add an explicit zero-check in `getRsETHAmountToMint()` mirroring the guard already present in `viewSwapAssetToPremintedRsETH()`:

```solidity
uint256 price = lrtOracle.rsETHPrice();
if (price == 0) revert InvalidRsETHPrice();
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / price;
```

Additionally, set `rsETHPrice = 1 ether` inside `LRTOracle.initialize()` so the contract is never in a zero-price state immediately after deployment.

### Proof of Concept
1. Deploy `LRTConfig`, `LRTOracle` (call `initialize()`), and `LRTDepositPool` (call `initialize()`).
2. Do **not** call `updateRSETHPrice()`.
3. Call `LRTDepositPool.depositETH{value: 1 ether}(0, "")`.
4. The call reverts: `lrtOracle.rsETHPrice()` returns `0`; the division `(1e18 * assetPrice) / 0` triggers an EVM division-by-zero panic, blocking the deposit.

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

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

**File:** contracts/LRTOracle.sol (L64-68)
```text
    function initialize(address lrtConfigAddr) external initializer {
        UtilLib.checkNonZeroAddress(lrtConfigAddr);
        lrtConfig = ILRTConfig(lrtConfigAddr);
        emit UpdatedLRTConfig(lrtConfigAddr);
    }
```

**File:** contracts/LRTOracle.sol (L214-222)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }
```

**File:** contracts/LRTOracle.sol (L248-250)
```text

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L421-427)
```text

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```
