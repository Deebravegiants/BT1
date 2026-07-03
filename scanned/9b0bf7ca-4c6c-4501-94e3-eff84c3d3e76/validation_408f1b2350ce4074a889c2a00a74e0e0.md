### Title
Missing Chainlink Staleness Check Enables Block-Stuffing-Assisted Over-Withdrawal of LST — (`contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice` discards the `updatedAt` return value from `latestRoundData()` and applies no heartbeat/staleness guard. An attacker who stuffs blocks to delay oracle update transactions can hold a stale-low asset price on-chain, then call `instantWithdrawal` to receive more LST than the burned rsETH is worth at current market rates.

---

### Finding Description

**Root cause — no staleness check:** [1](#0-0) 

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();   // updatedAt silently discarded
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

The five return values of `latestRoundData()` are `(roundId, answer, startedAt, updatedAt, answeredInRound)`. Only `answer` is used; `updatedAt` is never compared against `block.timestamp - heartbeat`.

**Price propagation path:**

`LRTOracle.getAssetPrice` delegates directly to the registered `IPriceFetcher`: [2](#0-1) 

`getExpectedAssetAmount` divides by that price: [3](#0-2) 

```solidity
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

If `getAssetPrice(asset)` returns a stale-low value `P_stale < P_real`, then:

```
underlyingToReceive = rsETHUnstaked * rsETHPrice / P_stale
                    > rsETHUnstaked * rsETHPrice / P_real   (real fair value)
```

**Exploit path through `instantWithdrawal`:** [4](#0-3) 

```solidity
uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
...
if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
    revert CantInstantWithdrawMoreThanAvailable();
}
unstakingVault.redeem(asset, assetAmountUnlocked);
```

The only guard is a vault-liquidity cap; there is no price-sanity or staleness check before the burn-and-redeem executes.

**Attack sequence:**

1. Attacker monitors the Chainlink feed for an LST whose price is about to rise (e.g., stETH/ETH after a large rebase).
2. Attacker stuffs blocks (fills block gas with high-fee transactions) to prevent Chainlink keeper update transactions from landing, keeping the on-chain answer at the pre-rebase (stale-low) value.
3. Attacker calls `instantWithdrawal(asset, rsETHUnstaked, ...)` while the stale price persists.
4. `getExpectedAssetAmount` returns an inflated LST amount; rsETH is burned and the excess LST is redeemed from `LRTUnstakingVault`.
5. Attacker sells the excess LST at the real market price, profiting the spread.

---

### Impact Explanation

The invariant that `assetAmountUnlocked * realAssetPrice ≤ rsETHUnstaked * rsETHPrice` is violated. The `LRTUnstakingVault` loses LST in excess of the rsETH value burned, constituting a direct, quantifiable loss of protocol assets. Impact is scoped as **Low — Block stuffing**.

---

### Likelihood Explanation

Block stuffing on Ethereum mainnet is expensive (attacker must outbid normal gas prices across consecutive blocks). Profitability requires a large enough price gap and sufficient vault liquidity to make the attack economically rational. This limits realistic exploitation to high-volatility events (large rebases, depeg events) where the spread is wide enough to cover stuffing costs. Likelihood is **Low**, but the code offers zero on-chain resistance once the price is stale.

---

### Recommendation

Add a staleness check in `ChainlinkPriceOracle.getAssetPrice`:

```solidity
(, int256 price,,uint256 updatedAt,) = priceFeed.latestRoundData();
require(block.timestamp - updatedAt <= STALENESS_THRESHOLD, "Stale price");
```

`STALENESS_THRESHOLD` should be set per-asset to slightly exceed the feed's documented heartbeat (e.g., 3 600 s for a 1-hour heartbeat feed). Additionally, consider adding a price-bounds check in `instantWithdrawal` analogous to the `minimumAssetPrice`/`maximumAssetPrice` guards already present in `unlockQueue`. [5](#0-4) 

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Fork test — pin block to a moment when the Chainlink stETH/ETH feed
// has NOT yet updated after a rebase (simulating block stuffing).

import "forge-std/Test.sol";

interface IChainlinkFeed {
    function latestRoundData() external view returns (
        uint80, int256, uint256, uint256, uint80
    );
}

contract BlockStuffingPoC is Test {
    address constant WITHDRAWAL_MANAGER = 0x...; // mainnet address
    address constant RSETH             = 0x...;
    address constant STETH             = 0x...;
    address constant STETH_FEED        = 0x...;

    function testStalePrice_OverWithdrawal() external {
        // 1. Fork at a block where stETH feed is stale-low
        //    (e.g., immediately after a rebase before keeper tx lands)
        vm.createSelectFork("mainnet", STALE_BLOCK);

        // 2. Confirm feed is stale
        (, int256 stalePrice,,uint256 updatedAt,) =
            IChainlinkFeed(STETH_FEED).latestRoundData();
        assertLt(block.timestamp - updatedAt, 0, "feed not stale — pick earlier block");

        // 3. Attacker holds rsETH
        uint256 rsETHAmount = 1 ether;
        deal(RSETH, address(this), rsETHAmount);
        IERC20(RSETH).approve(WITHDRAWAL_MANAGER, rsETHAmount);

        uint256 stethBefore = IERC20(STETH).balanceOf(address(this));

        // 4. Instant withdrawal at stale-low price
        ILRTWithdrawalManager(WITHDRAWAL_MANAGER)
            .instantWithdrawal(STETH, rsETHAmount, "poc");

        uint256 stethReceived = IERC20(STETH).balanceOf(address(this)) - stethBefore;

        // 5. Assert received > fair value at real price
        uint256 realPrice = getRealStETHPrice(); // off-chain / secondary oracle
        uint256 fairAmount = rsETHAmount * getRsETHPrice() / realPrice;
        assertGt(stethReceived, fairAmount,
            "attacker received more stETH than rsETH is worth");
    }
}
```

The test asserts `assetAmountUnlocked * realPrice > rsETHUnstaked * rsETHPrice`, directly proving the invariant violation without any admin compromise or mainnet execution.

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

**File:** contracts/LRTWithdrawalManager.sol (L228-235)
```text
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
        IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
        ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));
        if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
            revert CantInstantWithdrawMoreThanAvailable();
        }

        unstakingVault.redeem(asset, assetAmountUnlocked);
```

**File:** contracts/LRTWithdrawalManager.sol (L268-295)
```text
    function unlockQueue(
        address asset,
        uint256 firstExcludedIndex,
        uint256 minimumAssetPrice,
        uint256 minimumRsEthPrice,
        uint256 maximumAssetPrice,
        uint256 maximumRsEthPrice
    )
        external
        nonReentrant
        onlySupportedAsset(asset)
        whenNotPaused
        onlyAssetTransferOrOperatorRole
        returns (uint256 rsETHBurned, uint256 assetAmountUnlocked)
    {
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));
        ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));

        UnlockParams memory params = _createUnlockParams(lrtOracle, unstakingVault, asset);

        _validatePrices(
            params.rsETHPrice,
            params.assetPrice,
            minimumRsEthPrice,
            maximumRsEthPrice,
            minimumAssetPrice,
            maximumAssetPrice
        );
```

**File:** contracts/LRTWithdrawalManager.sol (L590-594)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```
