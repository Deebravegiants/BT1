### Title
Unprotected `latestRoundData()` Call in `ChainlinkPriceOracle` Causes Temporary Freezing of Deposits and Withdrawals - (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` on a Chainlink price feed without a `try/catch` guard. If the Chainlink multisig blocks access to the feed, the call reverts, propagating up through `LRTOracle.getAssetPrice()` into every user-facing deposit and withdrawal function, temporarily freezing all protocol activity for the affected asset.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` makes a bare external call to `priceFeed.latestRoundData()`:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L49-L55
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();   // <-- no try/catch
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
``` [1](#0-0) 

`LRTOracle.getAssetPrice()` delegates directly to this oracle:

```solidity
// contracts/LRTOracle.sol L156-L158
function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
    return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
}
``` [2](#0-1) 

`LRTOracle.getAssetPrice()` is consumed in two critical user-facing paths:

**1. Deposit path** — `LRTDepositPool.getRsETHAmountToMint()` (called by `depositETH` and `depositAsset`):

```solidity
// contracts/LRTDepositPool.sol L519-L520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [3](#0-2) 

**2. Withdrawal path** — `LRTWithdrawalManager.getExpectedAssetAmount()` (called by `initiateWithdrawal` and `instantWithdrawal`):

```solidity
// contracts/LRTWithdrawalManager.sol L592-L593
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
``` [4](#0-3) 

A second instance of the same pattern exists in `ChainlinkOracleForRSETHPoolCollateral.getRate()`, which is used by `RSETHPoolV3` pool deposits:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol L27-L28
(uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
    AggregatorV3Interface(oracle).latestRoundData();  // <-- no try/catch
``` [5](#0-4) 

---

### Impact Explanation

**Medium — Temporary freezing of funds.**

If the Chainlink multisig blocks access to the price feed for any supported LST (e.g., stETH, ETHx):

- `depositAsset()` reverts for that asset — users cannot deposit.
- `initiateWithdrawal()` reverts — users cannot queue new withdrawals.
- `instantWithdrawal()` reverts — users cannot instantly redeem rsETH for the affected asset.

Funds already in the protocol are not lost, but they are inaccessible for the duration of the outage, satisfying the **temporary freezing of funds** impact class.

---

### Likelihood Explanation

Chainlink multisigs have the documented ability to block access to price feeds (e.g., during oracle migrations or emergency interventions). This is a known, non-hypothetical operational scenario. No attacker action is required — the trigger is an external infrastructure event. The affected code paths are exercised by every ordinary depositor and withdrawer, so the blast radius is protocol-wide for the affected asset.

---

### Recommendation

Wrap the `latestRoundData()` call in a `try/catch` block in `ChainlinkPriceOracle.getAssetPrice()` and in `ChainlinkOracleForRSETHPoolCollateral.getRate()`. On failure, revert with a descriptive error rather than propagating an opaque revert from the oracle:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    try priceFeed.latestRoundData() returns (uint80, int256 price, uint256, uint256, uint80) {
        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    } catch {
        revert("ChainlinkPriceOracle: oracle call failed");
    }
}
```

Apply the same pattern to `ChainlinkOracleForRSETHPoolCollateral.getRate()`.

---

### Proof of Concept

1. Chainlink multisig blocks access to the stETH/ETH price feed.
2. Any user calls `LRTDepositPool.depositAsset(stETH, amount, minRSETH, "")`.
3. Execution reaches `getRsETHAmountToMint()` → `lrtOracle.getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` → `priceFeed.latestRoundData()` → **reverts**.
4. The entire transaction reverts. No stETH deposits are possible.
5. Simultaneously, any user calling `initiateWithdrawal(stETH, rsETHAmount, "")` hits the same revert path via `getExpectedAssetAmount()` → `lrtOracle.getAssetPrice(stETH)`.
6. All stETH deposit and withdrawal initiation is frozen for the duration of the oracle outage. [1](#0-0) [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
```

**File:** contracts/LRTDepositPool.sol (L99-118)
```text
    function depositAsset(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedERC20Token(asset)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L515-521)
```text
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L150-178)
```text
    function initiateWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        override
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
    {
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }

        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);

        emit ReferralIdEmitted(referralId);
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

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L26-36)
```text
    function getRate() public view returns (uint256) {
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
```
