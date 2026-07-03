### Title
Complete Absence of Chainlink Price Staleness Check Allows Indefinitely Stale Oracle Prices - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but silently discards the `updatedAt` timestamp, performing zero staleness validation. Unlike the reference report which at least enforced `heartbeat + buffer`, this contract imposes no time-bound whatsoever on how old a price can be. A stale Chainlink price is consumed directly by `LRTDepositPool.depositAsset()` and `LRTWithdrawalManager.initiateWithdrawal()`, both of which are permissionless user entry points.

### Finding Description
In `contracts/oracles/ChainlinkPriceOracle.sol`, `getAssetPrice()` destructures the five return values of `latestRoundData()` but binds only `price`, leaving `updatedAt` unnamed and unused:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();   // updatedAt silently dropped
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
``` [1](#0-0) 

`LRTOracle.getAssetPrice()` delegates directly to this oracle with no additional staleness guard:

```solidity
function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
    return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
}
``` [2](#0-1) 

The stale price then propagates into two critical user-facing paths:

**Deposit path** — `LRTDepositPool.getRsETHAmountToMint()` uses `lrtOracle.getAssetPrice(asset)` to compute how many rsETH tokens to mint per unit of deposited LST: [3](#0-2) 

**Withdrawal path** — `LRTWithdrawalManager.getExpectedAssetAmount()` uses `lrtOracle.getAssetPrice(asset)` to compute how many LST tokens a user receives when burning rsETH: [4](#0-3) 

Both `depositAsset()` and `initiateWithdrawal()` are callable by any unprivileged user with no role restriction. [5](#0-4) [6](#0-5) 

### Impact Explanation
**Severity: Critical — Direct theft of user funds.**

If a Chainlink feed for a supported LST (e.g., stETH/ETH) becomes stale while the real market price drops (e.g., a depeg event):

1. The oracle continues returning the last reported (inflated) price indefinitely.
2. An attacker buys the depegged LST cheaply on the open market.
3. The attacker calls `depositAsset()` with the cheap LST; `getRsETHAmountToMint()` prices it at the stale inflated rate, minting excess rsETH.
4. The attacker redeems the excess rsETH for ETH or other assets at fair value via `initiateWithdrawal()` or `instantWithdrawal()`.
5. The protocol is left holding overvalued collateral, directly socialising losses onto honest depositors.

The inverse also holds: if the stale price is lower than the real price, an attacker can call `initiateWithdrawal()` to lock in a favourable (inflated) asset-per-rsETH ratio computed at withdrawal initiation time.

### Likelihood Explanation
**Likelihood: Medium.**

Chainlink oracle staleness is a known, recurring event caused by network congestion, oracle node failures, or extreme market volatility. LST depeg events (stETH, rETH) have occurred historically. Because the protocol imposes no time bound at all, any period of oracle inactivity — however brief — is immediately exploitable. No special permissions are required; any EOA can trigger the attack.

### Recommendation
Add a heartbeat-based staleness check inside `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
mapping(address asset => uint256 heartbeat) public assetHeartbeat;

uint256 public constant STALENESS_BUFFER = 1 hours;

function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,, uint256 updatedAt,) = priceFeed.latestRoundData();

    uint256 heartbeat = assetHeartbeat[asset];
    if (heartbeat > 0 && block.timestamp - updatedAt > heartbeat + STALENESS_BUFFER) {
        revert StalePriceFeed(asset);
    }

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Each asset's heartbeat should be set to match the Chainlink feed's documented update frequency (e.g., 86400 s for daily feeds, 3600 s for hourly feeds). The buffer should be kept small (≤ 1 hour) and ideally scaled proportionally to the heartbeat, as recommended in the reference report.

### Proof of Concept

1. Assume stETH/ETH Chainlink feed has a 24-hour heartbeat and was last updated at `T = 0`.
2. At `T = 25 hours`, the feed has not updated (oracle node failure). Real stETH price has dropped 5% to 0.95 ETH.
3. `ChainlinkPriceOracle.getAssetPrice(stETH)` still returns `1.00e18` (the stale price) because `updatedAt` is never checked.
4. Attacker buys 1000 stETH on the open market for 950 ETH.
5. Attacker calls `LRTDepositPool.depositAsset(stETH, 1000e18, 0, "")`.
6. `getRsETHAmountToMint` computes: `(1000e18 * 1.00e18) / rsETHPrice` — minting rsETH worth 1000 ETH of collateral.
7. Attacker redeems rsETH for 1000 ETH worth of assets, netting ~50 ETH profit at the expense of the protocol.
8. The attack requires no privileged role and is executable by any EOA as soon as the oracle goes stale.

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

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
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

**File:** contracts/LRTWithdrawalManager.sol (L590-593)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```
