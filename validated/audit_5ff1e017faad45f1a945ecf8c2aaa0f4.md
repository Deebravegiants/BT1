### Title
Incorrect Decimal Handling in Token-to-rsETH Swap Calculation Causes Incorrect wrsETH Minting for Non-18 Decimal Tokens - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
`RSETHPoolV3.viewSwapRsETHAmountAndFee(uint256 amount, address token)` multiplies a raw token amount (in the token's native decimals) directly by a rate expressed as "ETH per 1 whole token" (18-decimal precision), without normalizing the token amount to 18 decimals first. For any supported token with decimals ≠ 18, the minted wrsETH amount is off by a factor of `10^(18 - tokenDecimals)`.

### Finding Description

The token-deposit path in `RSETHPoolV3` computes the wrsETH amount as:

```solidity
// contracts/pools/RSETHPoolV3.sol L324-334
fee = amount * feeBps / 10_000;
uint256 amountAfterFee = amount - fee;

uint256 rsETHToETHrate = getRate();                                    // e.g. 1e18
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate(); // e.g. 20e18 for WBTC

rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

`tokenToETHRate` is the price of **1 whole token** expressed in 18-decimal ETH (confirmed by `WETHOracle.getRate()` returning `1e18` for WETH). However, `amountAfterFee` is in the token's **native** decimals. For WBTC (8 decimals):

| Variable | Value | Meaning |
|---|---|---|
| `amountAfterFee` | `1e8` | 1 WBTC in satoshis |
| `tokenToETHRate` | `20e18` | 1 WBTC = 20 ETH |
| `rsETHToETHrate` | `1e18` | 1 rsETH ≈ 1 ETH |
| **Actual result** | `20e8` | 0.000000002 wrsETH |
| **Expected result** | `20e18` | 20 wrsETH |

The user receives `1e10` times fewer wrsETH than they are owed. The correct formula requires normalizing `amountAfterFee` to 18 decimals: `amountAfterFee * 10^(18 - tokenDecimals) * tokenToETHRate / rsETHToETHrate`.

The same root cause exists in the reverse-quote path:

```solidity
// contracts/pools/RSETHPoolV3.sol L400
tokenAmount = rsETHAmount * rsETHToETHrate / tokenToETHRate;
```

For WBTC this returns `1e18` units instead of `1e8`, i.e. `1e10` times more WBTC than owed.

The identical decimal-blindness also appears in `LRTDepositPool`:

```solidity
// contracts/LRTDepositPool.sol L520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();

// contracts/LRTDepositPool.sol L560
return lrtOracle.getAssetPrice(fromAsset) * fromAssetAmount / 1e18;
```

And in `LRTOracle._getTotalEthInProtocol`, where the comment itself acknowledges the assumption that is violated:

```solidity
// contracts/LRTOracle.sol L340-343
// totalAssetAmt is in 1e18 precision (standard token decimals)   ← incorrect for WBTC
uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```

### Impact Explanation

**Impact: Critical — direct theft of depositor funds.**

A user depositing 1 WBTC (≈ 20 ETH) via `RSETHPoolV3.deposit(token, amount, referralId)` receives `20e8` wrsETH instead of `20e18` wrsETH. The pool retains the full WBTC balance while the depositor holds tokens worth `1e10` times less than their deposit. The excess value accrues to the pool and benefits existing wrsETH holders at the depositor's expense.

If the same decimal-blind path is triggered in `LRTDepositPool`, `_getTotalEthInProtocol` computes a TVL `1e10` times smaller than reality, collapsing the rsETH price and corrupting the price oracle for all rsETH holders — a protocol-insolvency-class impact.

### Likelihood Explanation

**Likelihood: Low.**

The vulnerability is latent: it activates only when a token with decimals ≠ 18 is added via `RSETHPoolV3.addSupportedToken` (callable by `TIMELOCK_ROLE`) or as a supported asset in `LRTConfig`. All currently deployed supported assets (stETH, rETH, sfrxETH, swETH, ETHx, WETH) have 18 decimals. However, `RSETHPoolV3` has no on-chain guard preventing a non-18-decimal token from being added, and the protocol documentation references WBTC (8 decimals) as a candidate asset.

### Recommendation

Normalize token amounts to 18 decimals before performing rate arithmetic. Retrieve the token's decimals and scale accordingly:

```solidity
uint8 tokenDecimals = IERC20Metadata(token).decimals();
uint256 normalizedAmount = amountAfterFee * 10 ** (18 - tokenDecimals);
rsETHAmount = normalizedAmount * tokenToETHRate / rsETHToETHrate;
```

Apply the same normalization in `LRTDepositPool.getRsETHAmountToMint`, `getSwapAssetForETHReturnAmount`, `getSwapETHToAssetReturnAmount`, and `LRTOracle._getTotalEthInProtocol`.

### Proof of Concept

1. Admin calls `RSETHPoolV3.addSupportedToken(WBTC, wbtcOracle)` where `wbtcOracle.getRate()` returns `20e18` (1 WBTC = 20 ETH).
2. User approves `RSETHPoolV3` for `1e8` WBTC (1 WBTC).
3. User calls `RSETHPoolV3.deposit(WBTC, 1e8, "")`.
4. Inside `viewSwapRsETHAmountAndFee(1e8, WBTC)`:
   - `amountAfterFee = 1e8` (assuming 0 fee)
   - `tokenToETHRate = 20e18`
   - `rsETHToETHrate = 1e18`
   - `rsETHAmount = 1e8 * 20e18 / 1e18 = 20e8`
5. `wrsETH.mint(user, 20e8)` — user receives `20e8` wrsETH (≈ 0.000000002 wrsETH).
6. Expected: `20e18` wrsETH (20 wrsETH).
7. The pool holds 1 WBTC (≈ 20 ETH) while the user holds wrsETH worth ≈ `20e8 * 1e18 / 1e18 = 20e8` wei ≈ 0 ETH. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

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

**File:** contracts/pools/RSETHPoolV3.sol (L382-401)
```text
    function viewSwapAssetToPremintedRsETH(
        address token,
        uint256 rsETHAmount
    )
        public
        view
        onlySupportedTokenOrEth(token)
        returns (uint256 tokenAmount)
    {
        // Rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();
        if (rsETHToETHrate == 0) revert UnsupportedOracle();

        // Rate of token in ETH
        uint256 tokenToETHRate = token == ETH_IDENTIFIER ? 1e18 : IOracle(supportedTokenOracle[token]).getRate();
        if (tokenToETHRate == 0) revert UnsupportedOracle();

        // Calculate the amount of token user will get for the amount of rsETH
        tokenAmount = rsETHAmount * rsETHToETHrate / tokenToETHRate;
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

**File:** contracts/LRTDepositPool.sol (L549-561)
```text
    function getSwapAssetForETHReturnAmount(
        address fromAsset,
        uint256 fromAssetAmount
    )
        public
        view
        returns (uint256 returnAmount)
    {
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        return lrtOracle.getAssetPrice(fromAsset) * fromAssetAmount / 1e18;
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
