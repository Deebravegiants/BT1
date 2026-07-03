### Title
Missing Staleness Check in `ChainlinkPriceOracle` Allows Users to Receive Fewer Assets Than Fair Value in `instantWithdrawal` - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary

`ChainlinkPriceOracle.getAssetPrice()` fetches the Chainlink price without validating the `updatedAt` timestamp or `answeredInRound` field. When this stale price is consumed by `LRTWithdrawalManager.instantWithdrawal()`, users burn rsETH irreversibly but receive fewer underlying assets than the fair value of their rsETH, with no `minAmountOut` parameter to protect them.

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but silently discards all staleness indicators:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

The returned `updatedAt` timestamp and `answeredInRound` are never checked against a heartbeat or round-completeness condition. By contrast, the pool-level oracle wrapper `ChainlinkOracleForRSETHPoolCollateral` does perform both checks:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
``` [2](#0-1) 

`LRTWithdrawalManager.instantWithdrawal()` calls `getExpectedAssetAmount()`, which divides by the stale asset price:

```solidity
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
``` [3](#0-2) 

The rsETH is burned **before** the asset amount is validated:

```solidity
uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
``` [4](#0-3) 

There is no `minAmountOut` parameter in `instantWithdrawal` to let the user reject an unfavorable rate: [5](#0-4) 

### Impact Explanation

If the Chainlink feed for a supported LST (e.g., stETH/ETH) is stale and its last reported price is inflated relative to the current market price, `getAssetPrice(asset)` returns a value higher than reality. The division `rsETHPrice / assetPrice` then yields a **lower** `assetAmountUnlocked`. The user burns rsETH worth X ETH but receives assets worth less than X ETH. The rsETH burn is irreversible, so the user suffers a direct, unrecoverable loss. The shortfall accrues to the unstaking vault, benefiting remaining participants at the expense of the instant withdrawer.

**Impact: Low** — Contract fails to deliver promised returns; user receives fewer assets than the fair value of burned rsETH without any ability to set a floor.

### Likelihood Explanation

Chainlink heartbeats for LST/ETH feeds are typically 24 hours. During periods of network congestion, rapid LST price movement, or a temporary oracle outage, the on-chain price can lag the real price by a meaningful margin. Any user calling `instantWithdrawal` during such a window is silently penalized. The function is publicly callable by any rsETH holder whenever instant withdrawal is enabled.

**Likelihood: Medium** — Stale Chainlink prices are a known, recurring condition; the affected path is a standard user-facing withdrawal.

### Recommendation

1. Add a heartbeat/staleness check to `ChainlinkPriceOracle.getAssetPrice()`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:
   ```solidity
   (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
       priceFeed.latestRoundData();
   if (answeredInRound < roundId) revert StalePrice();
   if (block.timestamp - updatedAt > HEARTBEAT) revert StalePrice();
   ```
2. Add a `minAssetAmountOut` parameter to `instantWithdrawal()` so users can specify the minimum acceptable asset amount and revert if the oracle-derived amount falls below it, analogous to `minRSETHAmountExpected` in `LRTDepositPool.depositETH()`. [6](#0-5) 

### Proof of Concept

1. stETH/ETH Chainlink feed last updated 20 hours ago at price `1.05e18`; current real price is `1.00e18` (a 5% drop due to a slashing event).
2. User calls `instantWithdrawal(stETH, 1e18 rsETH, "")`.
3. `getExpectedAssetAmount` computes `1e18 * rsETHPrice / 1.05e18` → user receives ~4.76% fewer stETH than fair value.
4. rsETH is burned at line 229; the user cannot recover the difference.
5. No revert occurs because `ChainlinkPriceOracle` never checks `updatedAt` and `instantWithdrawal` has no `minAmountOut` guard.

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L50-54)
```text
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L30-32)
```text
        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();
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

**File:** contracts/LRTWithdrawalManager.sol (L592-593)
```text
        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

**File:** contracts/LRTDepositPool.sol (L76-92)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
```
