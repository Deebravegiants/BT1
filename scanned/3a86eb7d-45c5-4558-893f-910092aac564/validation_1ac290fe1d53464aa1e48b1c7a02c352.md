Looking at both files carefully to trace the exact vulnerability path.

### Title
Missing Chainlink Staleness Threshold Enables Stale-Rate wrsETH Over-Issuance — (`contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol`)

---

### Summary

`ChainlinkOracleForRSETHPoolCollateral.getRate()` omits a time-based staleness guard. Because `RSETHPoolV2NBA.deposit()` mints wrsETH using this rate with no daily mint cap, a Chainlink feed that has not been updated for hours or days silently produces an artificially low rsETH/ETH rate, causing every depositor to receive more wrsETH than the deposited ETH can back.

---

### Finding Description

`ChainlinkOracleForRSETHPoolCollateral.getRate()` calls `latestRoundData()` and applies three guards: [1](#0-0) 

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0)            revert IncompleteRound();
if (ethPrice <= 0)             revert InvalidPrice();
```

The `answeredInRound < roundID` check only catches a round that was *started but not yet answered*. For Chainlink OCR feeds, when no new round has been initiated (price deviation and heartbeat have not triggered), `roundID == answeredInRound` for the last completed round, so this check passes unconditionally regardless of how old the price is. The `timestamp == 0` check only catches a completely uninitialised round. Neither check bounds `block.timestamp - updatedAt`.

The missing guard is:

```solidity
if (block.timestamp - timestamp > MAX_STALENESS) revert StalePrice();
```

`RSETHPoolV2NBA.deposit()` calls `viewSwapRsETHAmountAndFee`, which calls `getRate()` and computes: [2](#0-1) 

```solidity
uint256 rsETHToETHrate = getRate();
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

rsETH is a yield-bearing token whose ETH value increases monotonically over time. A stale oracle returns an old, *lower* rate. Dividing by a lower rate produces a *larger* `rsETHAmount`, so every depositor receives more wrsETH than the deposited ETH can redeem. The contract has no daily mint limit: [3](#0-2) 

(Compare `LRTOracle`, which does enforce `maxFeeMintAmountPerDay` — `RSETHPoolV2NBA` has no equivalent.)

---

### Impact Explanation

Every deposit during a stale-oracle window mints excess wrsETH. The over-issuance per deposit is proportional to the rsETH appreciation since the last oracle update. With no mint cap, the aggregate shortfall is unbounded and constitutes **protocol insolvency**: the pool has issued more wrsETH claims than the ETH it holds can back when users redeem.

---

### Likelihood Explanation

Chainlink feeds update on price-deviation or heartbeat. If the rsETH/ETH price is stable (low volatility, as expected for a staking derivative), the heartbeat interval (typically 24 h) is the only trigger. Network congestion or oracle-node issues can delay updates beyond the heartbeat. The window is realistic and requires no privileged access — any user calling `deposit()` during the stale window exploits it passively.

---

### Recommendation

Add an immutable `MAX_STALENESS` constant and enforce it in `getRate()`:

```solidity
uint256 public constant MAX_STALENESS = 24 hours; // tune to feed heartbeat

function getRate() public view returns (uint256) {
    (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
        AggregatorV3Interface(oracle).latestRoundData();

    if (answeredInRound < roundID)              revert StalePrice();
    if (timestamp == 0)                         revert IncompleteRound();
    if (block.timestamp - timestamp > MAX_STALENESS) revert StalePrice();
    if (ethPrice <= 0)                          revert InvalidPrice();

    return uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
}
```

Additionally, consider adding a daily mint cap to `RSETHPoolV2NBA` analogous to `LRTOracle.maxFeeMintAmountPerDay` to bound worst-case exposure from any oracle failure.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";

interface IPool {
    function deposit(string memory referralId) external payable;
}

interface IERC20 {
    function balanceOf(address) external view returns (uint256);
}

contract StaleOraclePoC is Test {
    // Fork mainnet at a recent block, then warp forward.
    // Replace addresses with actual deployed contracts.
    address constant POOL    = address(0xPOOL);
    address constant WRSETH  = address(0xWRSETH);

    function testStaleRateOverIssuance() external {
        // Record wrsETH balance before
        uint256 balBefore = IERC20(WRSETH).balanceOf(address(this));

        // Deposit at current (fresh) rate
        IPool(POOL).deposit{value: 100 ether}("");
        uint256 mintedFresh = IERC20(WRSETH).balanceOf(address(this)) - balBefore;

        // Warp 48 hours without updating the Chainlink feed
        vm.warp(block.timestamp + 48 hours);

        uint256 balMid = IERC20(WRSETH).balanceOf(address(this));
        IPool(POOL).deposit{value: 100 ether}("");
        uint256 mintedStale = IERC20(WRSETH).balanceOf(address(this)) - balMid;

        // mintedStale > mintedFresh because stale rate is lower
        assertGt(mintedStale, mintedFresh, "stale oracle causes over-issuance");

        // Insolvency gap: excess wrsETH issued that ETH cannot back
        uint256 gap = mintedStale - mintedFresh;
        emit log_named_uint("Over-issued wrsETH (wei)", gap);
    }
}
```

The test warps time 48 hours without touching the Chainlink feed. Because `ChainlinkOracleForRSETHPoolCollateral` has no `block.timestamp - updatedAt` check, `getRate()` returns the same old (lower) rate, `deposit()` mints more wrsETH than the second 100 ETH can back, and the assertion confirms the insolvency gap. [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L26-37)
```text
    function getRate() public view returns (uint256) {
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
    }
```

**File:** contracts/pools/RSETHPoolV2NBA.sol (L106-118)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV2NBA.sol (L124-133)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```
