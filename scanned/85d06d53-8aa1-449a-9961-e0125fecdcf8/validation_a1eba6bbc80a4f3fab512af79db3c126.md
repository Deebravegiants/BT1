### Title
Missing Decimal Normalization in Token-to-rsETH Swap Calculation Causes Massive Fund Loss for Non-18-Decimal Token Depositors - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
The `viewSwapRsETHAmountAndFee(uint256 amount, address token)` function in `RSETHPoolV3` (and all sibling pool contracts) computes the rsETH output by multiplying the raw token amount directly against a 1e18-normalized oracle rate, without first scaling the token amount to 18 decimals. When a supported token has fewer than 18 decimals (e.g., USDC with 6, wBTC with 8), the user receives `10^(18 - tokenDecimals)` times fewer rsETH than the fair value of their deposit. Their tokens are permanently absorbed by the pool while they receive a negligible rsETH balance.

### Finding Description
`ChainlinkOracleForRSETHPoolCollateral.getRate()` returns the price of **one whole token** in ETH, normalized to 1e18 precision:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol L34
uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
```

This is the price of 1 whole USDC (= 1e6 units) in ETH, expressed with 1e18 precision. The pool's swap calculation then does:

```solidity
// contracts/pools/RSETHPoolV3.sol L324-L334
fee = amount * feeBps / 10_000;
uint256 amountAfterFee = amount - fee;
uint256 rsETHToETHrate = getRate();
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

`amountAfterFee` is in the token's native units (e.g., 1e6 for 1 USDC). `tokenToETHRate` is the price of 1 **whole** token in ETH (1e18 precision). The formula implicitly treats `amountAfterFee` as if it were already in 18-decimal units, which it is not for sub-18-decimal tokens.

**Concrete arithmetic for 1 USDC deposit (6 decimals):**
- `amountAfterFee` = 1e6 (1 USDC in units)
- `tokenToETHRate` ≈ 3.3e14 (1 USDC ≈ 0.00033 ETH, in 1e18 precision)
- `rsETHToETHrate` ≈ 1.05e18

Actual result: `1e6 * 3.3e14 / 1.05e18 ≈ 314` rsETH units (= 3.14e-16 rsETH)

Correct result: `(1e6 / 1e6) * 3.3e14 / 1.05e18 * 1e18 ≈ 3.14e14` rsETH units (= 0.000314 rsETH)

The user receives `10^12` times fewer rsETH than fair value. The same root cause exists identically in `RSETHPoolV3WithNativeChainBridge`, `RSETHPoolV3ExternalBridge`, `RSETHPoolNoWrapper`, `RSETHPool`, and `AGETHPoolV3`.

The same pattern also appears in `LRTDepositPool.getRsETHAmountToMint`:

```solidity
// contracts/LRTDepositPool.sol L520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

### Impact Explanation
**Critical — Direct theft of user funds.** A user depositing any supported non-18-decimal token (e.g., USDC, USDT, wBTC) receives a negligible rsETH balance while their full token deposit is absorbed into the pool. The excess ETH-equivalent value accrues to the pool's TVL, benefiting all other rsETH holders at the depositor's expense. The depositor's tokens are permanently lost relative to the rsETH they receive, as the rsETH they hold is worth orders of magnitude less than what they deposited.

### Likelihood Explanation
**Medium.** The pool contracts are explicitly designed to support arbitrary ERC20 tokens via `supportedTokenOracle`. The admin can add any token with a Chainlink oracle at any time — this is a routine operational action, not a compromise. Non-18-decimal tokens (USDC, USDT, wBTC) are among the most commonly integrated assets in DeFi protocols. Any depositor using such a token after it is added triggers the loss with no further conditions.

### Recommendation
Normalize `amountAfterFee` to 18 decimals before applying the oracle rate:

```solidity
uint8 tokenDecimals = IERC20Metadata(token).decimals();
uint256 normalizedAmount = amountAfterFee * 10 ** (18 - tokenDecimals);
rsETHAmount = normalizedAmount * tokenToETHRate / rsETHToETHrate;
```

Apply the same fix to `LRTDepositPool.getRsETHAmountToMint` and all sibling pool contracts. Add integration tests covering 6-decimal and 8-decimal token deposits to prevent regression.

### Proof of Concept

1. Admin calls `addSupportedToken(USDC_ADDRESS, chainlinkUSDCETHOracle)` on `RSETHPoolV3`.
2. User calls `deposit(USDC_ADDRESS, 1_000_000, "ref")` (depositing 1 USDC = 1e6 units).
3. `viewSwapRsETHAmountAndFee(1_000_000, USDC_ADDRESS)` executes:
   - `fee = 1_000_000 * feeBps / 10_000` (small)
   - `amountAfterFee ≈ 1_000_000`
   - `tokenToETHRate = getRate()` ≈ 3.3e14 (1 USDC in ETH, 1e18 precision)
   - `rsETHToETHrate ≈ 1.05e18`
   - `rsETHAmount = 1_000_000 * 3.3e14 / 1.05e18 ≈ 314`
4. User receives 314 units of wrsETH (= 3.14e-16 rsETH, worth ~1e-13 USD).
5. User's 1 USDC (worth ~$1) is permanently in the pool. Loss factor: `10^12`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L315-334)
```text
    function viewSwapRsETHAmountAndFee(
        uint256 amount,
        address token
    )
        public
        view
        onlySupportedToken(token)
        returns (uint256 rsETHAmount, uint256 fee)
    {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

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

**File:** contracts/agETH/AGETHPoolV3.sol (L175-195)
```text
    function viewSwapAgETHAmountAndFee(
        uint256 amount,
        address token
    )
        public
        view
        onlySupportedToken(token)
        returns (uint256 agETHAmount, uint256 fee)
    {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of agETH in ETH
        uint256 agETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final agETH amount
        agETHAmount = amountAfterFee * tokenToETHRate / agETHToETHrate;
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
