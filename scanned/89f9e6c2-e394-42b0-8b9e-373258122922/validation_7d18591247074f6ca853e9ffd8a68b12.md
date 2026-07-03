### Title
Chainlink Market Rate Feed for stETH Enables Deposit/Withdrawal Arbitrage - (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

The `ChainlinkPriceOracle` uses the Chainlink stETH/ETH **market rate** feed (secondary market price) for stETH, while every other LST oracle in the protocol uses a protocol-internal **exchange rate** feed. When stETH trades at a discount on secondary markets, the protocol's TVL is undervalued, rsETH price is depressed, and an unprivileged attacker can deposit ETH at the artificially low rsETH price and withdraw stETH at the depressed market rate — extracting value from existing rsETH holders.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` on whatever Chainlink aggregator is configured per asset: [1](#0-0) 

For stETH, the Chainlink stETH/ETH feed is a **market rate** feed — it tracks secondary market prices (e.g., Curve pool) and can depeg from the Lido protocol's internal exchange rate. There is no dedicated stETH oracle adapter in the codebase (unlike rETH, swETH, sfrxETH, and EthX, which all have dedicated adapters calling protocol-internal exchange rate functions): [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

All four use protocol-internal rates that cannot depeg. stETH, having no dedicated adapter, is priced via `ChainlinkPriceOracle` with the market rate feed.

The rsETH price is computed by `LRTOracle._updateRsETHPrice()` as `totalETHInProtocol / rsETHSupply`, where `totalETHInProtocol` sums each asset's balance multiplied by its oracle price: [6](#0-5) 

When stETH depegs, `getAssetPrice(stETH)` returns the depressed market rate, TVL is undervalued, and `rsETHPrice` drops after `updateRSETHPrice()` is called (a public function, callable by anyone): [7](#0-6) 

The deposit path mints rsETH using the stored (now depressed) rsETH price: [8](#0-7) 

The withdrawal path computes the stETH payout using the same depressed prices: [9](#0-8) 

The `_calculatePayoutAmount` function at unlock time takes the **minimum** of the expected amount (locked in at initiation) and the current return, providing partial but incomplete protection: [10](#0-9) 

If `isInstantWithdrawalEnabled[stETH]` is true, the 8-day delay is bypassed entirely via `instantWithdrawal()`: [11](#0-10) 

---

### Impact Explanation

When stETH depegs (market rate < exchange rate), existing rsETH holders suffer dilution:

- The attacker deposits ETH (priced 1:1, unaffected by the depeg) at a time when rsETH price is artificially depressed, receiving **more rsETH per ETH than fair value**.
- The attacker then withdraws stETH, receiving stETH at the depressed market rate.
- After the market rate recovers, the attacker holds stETH worth more (at exchange rate) than the ETH they deposited.
- The excess rsETH minted to the attacker dilutes all existing rsETH holders, constituting **theft of unclaimed yield**.

Concrete example (April 13, 2024-style depeg, stETH market rate = 0.99 ETH, exchange rate = 1.01 ETH):
- Protocol TVL: 100 stETH × 0.99 = 99 ETH; rsETH supply = 100; rsETH price = 0.99 ETH.
- Attacker deposits 1 ETH → mints `1 / 0.99 = 1.0101 rsETH`.
- Attacker withdraws stETH: `expectedAssetAmount = 1.0101 × 0.99 / 0.99 = 1.0101 stETH`.
- At exchange rate: 1.0101 stETH = 1.0202 ETH → **~2% profit extracted from existing holders**.

**Impact**: High — theft of unclaimed yield from existing rsETH holders.

---

### Likelihood Explanation

stETH market rate depegs are documented real-world events (e.g., April 13, 2024, ~1% depeg). The attack requires no privileged access: `updateRSETHPrice()` is public, `depositETH()` and `depositAsset()` are open to any user, and `initiateWithdrawal()` / `instantWithdrawal()` are open to any rsETH holder. The 8-day delay reduces but does not eliminate the risk; if instant withdrawal is enabled for stETH, the attack is immediate and requires no waiting.

**Likelihood**: Medium — stETH depegs occur periodically; the attack path is fully permissionless.

---

### Recommendation

Replace the Chainlink stETH/ETH market rate feed with a protocol-internal exchange rate source for stETH. Lido exposes `stETH.getPooledEthByShares(1e18)` (or equivalently `stETH.tokensPerStEth()`) which returns the protocol-guaranteed exchange rate and cannot be manipulated by secondary market sentiment. A dedicated `StETHPriceOracle` adapter (analogous to `RETHPriceOracle`, `SwETHPriceOracle`, etc.) should be created that calls this function, ensuring consistency with all other LST oracle adapters in the protocol.

---

### Proof of Concept

**Attack path (without instant withdrawal, 8-day delay):**

1. stETH depegs on secondary markets (Chainlink stETH/ETH feed drops to 0.99 ETH; Lido internal rate = 1.01 ETH).
2. Attacker calls `LRTOracle.updateRSETHPrice()` — rsETH price drops to reflect the undervalued TVL.
3. Attacker calls `LRTDepositPool.depositETH{value: 1 ether}(0, "")` → receives `1e18 / 0.99e18 = 1.0101e18` rsETH (more than fair value).
4. Attacker calls `LRTWithdrawalManager.initiateWithdrawal(stETH, 1.0101e18, "")` → `expectedAssetAmount = 1.0101 × 0.99 / 0.99 = 1.0101 stETH` is locked in.
5. After 8 days, operator calls `unlockQueue(stETH, ...)`. If stETH has recovered to 1.01 ETH, `currentReturn = 1.0101 × recoveredRsETHPrice / 1.01`. The attacker still receives more stETH than the 1 ETH they deposited is worth at the recovered exchange rate.
6. Attacker calls `completeWithdrawal(stETH, "")` → receives stETH worth more than 1 ETH at exchange rate.

**Attack path (with instant withdrawal enabled):**

Steps 1–3 same as above. Then:

4. Attacker calls `LRTWithdrawalManager.instantWithdrawal(stETH, 1.0101e18, "")` → immediately receives 1.0101 stETH (minus instant withdrawal fee).
5. stETH market rate recovers; attacker holds 1.0101 stETH worth 1.0202 ETH at exchange rate — **~2% profit with no delay**.

### Citations

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

**File:** contracts/oracles/SwETHPriceOracle.sol (L34-40)
```text
    function getAssetPrice(address asset) external view returns (uint256) {
        if (asset != swETHAddress) {
            revert InvalidAsset();
        }

        return ISwETH(swETHAddress).getRate();
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

**File:** contracts/oracles/EthXPriceOracle.sol (L46-52)
```text
    function getAssetPrice(address asset) external view returns (uint256) {
        if (asset != ethxAddress) {
            revert InvalidAsset();
        }

        return IETHXStakePoolsManager(ethXStakePoolsManagerProxyAddress).getExchangeRate();
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
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

**File:** contracts/LRTDepositPool.sol (L516-521)
```text
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L212-253)
```text
    function instantWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
        onlyInstantWithdrawalAllowed(asset)
    {
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }
        if (IERC20(lrtConfig.rsETH()).balanceOf(msg.sender) < rsETHUnstaked) revert NotEnoughRsETH();
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
        IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
        ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));
        if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
            revert CantInstantWithdrawMoreThanAvailable();
        }

        unstakingVault.redeem(asset, assetAmountUnlocked);

        uint256 fee = (assetAmountUnlocked * instantWithdrawalFee) / 10_000;
        uint256 userAmount = assetAmountUnlocked - fee;

        address feeRecipient = instantWithdrawalFeeRecipient;
        if (feeRecipient == address(0)) {
            // Backwards-compatible default: send fees to the protocol treasury
            feeRecipient = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
        }
        if (fee > 0) {
            _transferAsset(asset, feeRecipient, fee);
            emit InstantWithdrawalFeeCollected(msg.sender, asset, fee);
        }

        _transferAsset(asset, msg.sender, userAmount);
        emit ReferralIdEmitted(referralId);
        emit AssetWithdrawalFinalized(msg.sender, asset, rsETHUnstaked, userAmount);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L589-594)
```text
        // setup oracle contract
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L824-835)
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
    }
```
