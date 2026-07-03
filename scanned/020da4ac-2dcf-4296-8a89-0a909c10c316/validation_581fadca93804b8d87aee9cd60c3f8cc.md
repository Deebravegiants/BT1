### Title
Token Decimal Mismatch in `viewSwapRsETHAmountAndFee` Causes Incorrect rsETH Minting for Non-18-Decimal Tokens - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
The `viewSwapRsETHAmountAndFee(amount, token)` function in all L2 pool contracts computes the rsETH output amount using raw token units directly against 1e18-normalized oracle rates, without normalizing for the deposited token's decimal precision. If a supported token has fewer than 18 decimals (e.g., USDC with 6), a depositor receives a negligible amount of wrsETH relative to the value deposited, effectively losing their funds to the pool.

### Finding Description
In `RSETHPoolV3.viewSwapRsETHAmountAndFee(uint256 amount, address token)`, the rsETH output is computed as:

```solidity
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
``` [1](#0-0) 

Both `tokenToETHRate` (from `IOracle(supportedTokenOracle[token]).getRate()`) and `rsETHToETHrate` (from `getRate()`) are 1e18-normalized exchange rates. The formula implicitly assumes `amountAfterFee` is also in 1e18 units — i.e., that the deposited token has 18 decimals. No decimal normalization is applied. [2](#0-1) 

The same pattern is present in every pool variant: [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) 

The `addSupportedToken` path imposes no constraint on token decimals: [7](#0-6) 

### Impact Explanation
**Critical — Direct theft of user funds.**

For a token with `d < 18` decimals (e.g., USDC, `d = 6`), the raw `amount` is `10^(18-d)` times smaller than the formula expects. The minted wrsETH is therefore `10^(18-d)` times smaller than the correct value.

Concrete example — depositing 1,000 USDC (1,000e6 raw units):
- `tokenToETHRate` ≈ 3e14 (1 USDC ≈ 0.0003 ETH, 1e18-normalized)
- `rsETHToETHrate` ≈ 1.05e18
- Computed: `1e9 × 3e14 / 1.05e18 ≈ 2.86e5` (≈ 2.86e-13 rsETH)
- Expected: `1,000 × 0.0003 / 1.05 ≈ 0.286 rsETH = 2.86e17`

The user's 1,000 USDC (~0.3 ETH of value) is transferred into the pool but they receive essentially zero wrsETH. The USDC remains in the pool with no mechanism for the user to recover it proportionally.

For a token with `d > 18` decimals the mismatch inverts: the user receives `10^(d-18)` times more wrsETH than deserved, draining the pool's pre-minted wrsETH supply and causing protocol insolvency.

### Likelihood Explanation
**Medium.** The pool contracts are explicitly designed to support arbitrary ERC20 tokens via `addSupportedToken`/`setSupportedTokenOracle`. USDC, USDT, and similar 6-decimal stablecoins are natural candidates for L2 liquidity pools. There is no on-chain guard against adding a non-18-decimal token, and the decimal assumption is undocumented, making silent misconfiguration by an operator realistic.

### Recommendation
Normalize `amountAfterFee` to 18 decimals before applying the oracle-rate formula:

```solidity
uint8 tokenDecimals = IERC20Metadata(token).decimals();
uint256 normalizedAmount = amountAfterFee * 10 ** (18 - tokenDecimals);
rsETHAmount = normalizedAmount * tokenToETHRate / rsETHToETHrate;
```

Apply the same fix to `feeEarnedInToken` accounting and to `LRTDepositPool.getRsETHAmountToMint` and `LRTOracle._getTotalEthInProtocol` for consistency if non-18-decimal assets are ever added to the L1 pool. [8](#0-7) [9](#0-8) 

### Proof of Concept
1. Deploy `RSETHPoolV3` on an L2 with a USDC oracle returning `3e14` (0.0003 ETH/USDC).
2. Call `addSupportedToken(USDC, usdcOracle, bridge)`.
3. Call `deposit(USDC, 1_000e6, "ref")` — transfers 1,000 USDC from the caller.
4. Observe `viewSwapRsETHAmountAndFee(1_000e6, USDC)` returns `rsETHAmount ≈ 285_714` (≈ 2.86e-13 rsETH in 18-decimal terms).
5. Expected output: `≈ 2.86e17` (0.286 rsETH). The user receives `1e12×` less wrsETH than owed; the 1,000 USDC is permanently stranded in the pool. [10](#0-9)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L271-293)
```text
    function deposit(
        address token,
        uint256 amount,
        string memory referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedToken(token)
        limitDailyMint(amount, token)
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L315-335)
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
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L571-589)
```text
     * @notice Sets the oracle for a specific token
     * @param token The token address
     * @param oracle The new oracle address for the token
     */
    function setSupportedTokenOracle(
        address token,
        address oracle
    )
        external
        onlyRole(TIMELOCK_ROLE)
        onlySupportedToken(token)
    {
        UtilLib.checkNonZeroAddress(oracle);
        if (IOracle(oracle).getRate() == 0) {
            revert UnsupportedOracle();
        }
        supportedTokenOracle[token] = oracle;
        emit TokenOracleSet(token, oracle);
    }
```

**File:** contracts/pools/RSETHPool.sol (L326-347)
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
        uint256 feeBpsForToken = tokenFeeBps[token];
        fee = amount * feeBpsForToken / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L292-312)
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
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L433-453)
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
    }
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L351-371)
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
    }
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L339-343)
```text
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```
