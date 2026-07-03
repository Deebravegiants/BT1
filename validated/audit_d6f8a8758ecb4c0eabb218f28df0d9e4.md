Audit Report

## Title
Missing Staleness Check on Cross-Chain Rate Allows Over-Minting of rsETH on Deposits — (`contracts/cross-chain/CrossChainRateReceiver.sol`)

## Summary
`CrossChainRateReceiver` stores `rate` and `lastUpdated` when a LayerZero message arrives, but `getRate()` returns `rate` unconditionally with no check against `lastUpdated`. All pool variants (`RSETHPoolV3`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPoolV3ExternalBridge`) use this stale-capable rate as the denominator in the rsETH minting formula, while the numerator uses a live Chainlink price. When the cross-chain rate lags behind true L1 rsETH appreciation, the denominator is artificially low and the pool mints more rsETH than the deposited collateral backs at the true rate, diluting existing rsETH holders.

## Finding Description
`CrossChainRateReceiver.lzReceive()` records `rate` and `lastUpdated` on each LayerZero delivery: [1](#0-0) 

`getRate()` returns `rate` with no staleness guard: [2](#0-1) 

`RSETHPoolV3.getRate()` delegates directly to this oracle: [3](#0-2) 

The minting formula in `viewSwapRsETHAmountAndFee`: [4](#0-3) 

The token-to-ETH rate comes from `ChainlinkOracleForRSETHPoolCollateral.getRate()`, which fetches a live Chainlink price with basic round-completeness checks but no time-based staleness bound: [5](#0-4) 

The same vulnerable pattern is present in `RSETHPoolV3WithNativeChainBridge`: [6](#0-5) 

The exploit path: (1) rsETH accrues staking yield on L1, raising the true rsETH/ETH rate; (2) the LZ keeper has not yet delivered an updated rate (delay, congestion, or cost); (3) an attacker calls `deposit(token, amount, referralId)` — a fully public, permissionless function; (4) `rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate` uses a stale-low denominator, minting more rsETH than the collateral backs at the true rate. No existing check prevents this: `lastUpdated` is stored but never read in any guard.

## Impact Explanation
The pool mints rsETH in excess of what the deposited collateral backs at the true current rate. Each over-minted unit dilutes the backing ratio for all existing rsETH holders. This matches **Low — contract fails to deliver correctly-backed promised returns**: the protocol's invariant (each rsETH is backed by an equivalent ETH value of collateral) is violated during any staleness window. The magnitude per deposit is bounded by the staking yield accrued since the last LZ update (e.g., ~0.008% per 24-hour gap at 3% APY), but it is repeatable and cumulative across all deposits during the window.

## Likelihood Explanation
Any unprivileged depositor can trigger this by calling the public `deposit` function during a staleness window. The LZ rate update is not automatic — it requires an off-chain keeper to call `updateRate()` and pay the LZ messaging fee. Keeper delays due to network congestion, gas cost, or operational gaps are normal operational conditions, not edge cases. rsETH accrues staking yield continuously, so a staleness window always exists between consecutive LZ deliveries.

## Recommendation
Add a staleness guard in `CrossChainRateReceiver.getRate()` that reverts if the stored rate is older than a configurable `MAX_RATE_AGE`:

```solidity
uint256 public maxRateAge; // e.g., set to 24 hours

function getRate() external view returns (uint256) {
    if (block.timestamp - lastUpdated > maxRateAge) revert StaleRate();
    return rate;
}
```

`maxRateAge` should be set to match the expected LZ update frequency with a reasonable buffer. This fix applies to all pool variants that inherit or delegate to `CrossChainRateReceiver`.

## Proof of Concept
```solidity
// Foundry fork test on an L2 where RSETHPoolV3 is deployed
function testStaleRateOverMint() public {
    // Simulate a stale rate: last LZ update was 2 days ago at 1.05e18
    // True current L1 rate is 1.06e18 (staking yield accrued)
    vm.store(address(rsETHRateReceiver), bytes32(uint256(0)), bytes32(uint256(1.05e18)));
    vm.store(address(rsETHRateReceiver), bytes32(uint256(1)), bytes32(block.timestamp - 2 days));

    // Chainlink wstETH/ETH returns fresh price: 1.15e18 (mocked or real fork value)
    uint256 depositAmount = 1e18;
    deal(address(wstETH), attacker, depositAmount);
    vm.startPrank(attacker);
    wstETH.approve(address(pool), depositAmount);
    pool.deposit(address(wstETH), depositAmount, "");
    vm.stopPrank();

    // At true rate 1.06e18: expected rsETH ≈ 1e18 * 1.15e18 / 1.06e18 ≈ 1.0849e18
    // At stale rate 1.05e18: actual rsETH  ≈ 1e18 * 1.15e18 / 1.05e18 ≈ 1.0952e18
    // Over-minted: ~0.0103e18 rsETH per wstETH deposited
    assertGt(wrsETH.balanceOf(attacker), 1.0849e18);
}
```

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L95-97)
```text
        rate = _rate;

        lastUpdated = block.timestamp;
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L102-105)
```text
    /// @notice Gets the last stored rate in the contract
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L234-237)
```text
    /// @dev Gets the rate from the rsETHOracle
    function getRate() public view returns (uint256) {
        return IOracle(rsETHOracle).getRate();
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L327-334)
```text
        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
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

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L363-370)
```text
        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```
