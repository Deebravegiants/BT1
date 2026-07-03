### Title
Unsafe `uint256(price)` Cast Without Sign Validation Enables Protocol Insolvency or Deposit/Withdrawal DoS - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` casts the raw `int256` Chainlink answer directly to `uint256` without first verifying `price > 0`. A zero or negative return from the feed produces either a zero price (division-by-zero DoS on withdrawals) or an astronomically large price (protocol insolvency via unbounded rsETH minting). The same codebase already applies the correct guard in `ChainlinkOracleForRSETHPoolCollateral.sol`, confirming this is a code-level oversight, not an intentional design choice.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` performs the following cast:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

There is no guard on `price`. Two failure modes exist:

- **`price == 0`**: `uint256(0) == 0`. Any downstream division by this value (e.g., `LRTWithdrawalManager.getExpectedAssetAmount`) reverts with division-by-zero, freezing all withdrawals for the affected asset.
- **`price < 0`**: Solidity's two's-complement reinterpretation turns `-1` into `type(uint256).max ≈ 1.15 × 10^77`. The returned "asset price" is astronomically large, allowing a depositor to mint a near-infinite amount of rsETH for a tiny LST deposit.

By contrast, `ChainlinkOracleForRSETHPoolCollateral.getRate()` — used for the same purpose in the L2 pool collateral path — explicitly guards the cast:

```solidity
if (ethPrice <= 0) revert InvalidPrice();
uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(...decimals());
``` [2](#0-1) 

The inconsistency is a code-level oversight in `ChainlinkPriceOracle`, not an external-only issue.

---

### Impact Explanation

`ChainlinkPriceOracle.getAssetPrice()` is the price source for all supported LSTs (stETH, ETHx, sfrxETH) on L1. It feeds directly into:

1. **`LRTDepositPool.getRsETHAmountToMint()`** — `rsETHAmount = (depositAmount × assetPrice) / rsETHPrice`. A hugely inflated `assetPrice` lets a depositor mint unbounded rsETH for a dust deposit, draining the protocol's backing and causing insolvency.

2. **`LRTWithdrawalManager.getExpectedAssetAmount()`** — `underlyingToReceive = rsETHAmount × rsETHPrice / assetPrice`. A zero `assetPrice` causes a division-by-zero revert, permanently blocking all withdrawal completions for the affected asset. [3](#0-2) 

---

### Likelihood Explanation

Chainlink feeds can legitimately return `0` in edge cases: feed deprecation, circuit-breaker activation, or a newly deployed feed with no round data. Negative answers are less common but are not impossible for misconfigured or deprecated feeds. The root cause — the missing `price > 0` guard — is entirely within the protocol's control and is already correctly applied elsewhere in the same codebase.

---

### Recommendation

Mirror the guard already present in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
if (price <= 0) revert InvalidPrice();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [4](#0-3) 

---

### Proof of Concept

1. Chainlink's LST/ETH feed returns `price = 0` (e.g., feed is deprecated or circuit-breaker fires).
2. `ChainlinkPriceOracle.getAssetPrice(stETH)` returns `0`.
3. Any call to `LRTWithdrawalManager.getExpectedAssetAmount(stETH, amount)` executes `amount * rsETHPrice / 0`, reverting with a division-by-zero panic.
4. All pending stETH withdrawal requests are permanently uncompletable — funds are frozen in the contract.

Alternatively, if `price = -1`:
- `uint256(-1) = 115792089237316195423570985008687907853269984665640564039457584007913129639935`
- `getAssetPrice(stETH)` returns `~1.15 × 10^95`
- A depositor calls `LRTDepositPool.depositAsset(stETH, 1 wei, 0, "")` and receives `(1 × 1.15e95) / rsETHPrice ≈ 1.15e77` rsETH, draining the entire protocol. [4](#0-3) [2](#0-1)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L32-34)
```text
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
```

**File:** contracts/LRTWithdrawalManager.sol (L590-593)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```
