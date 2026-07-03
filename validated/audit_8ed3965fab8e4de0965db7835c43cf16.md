### Title
Hardcoded 1e18 Decimal Assumption Causes Share/Asset Mis-accounting for Non-18 Decimal Tokens - (`contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`, `contracts/pools/RSETHPoolV3.sol`)

---

### Summary

The LRT-rsETH protocol hardcodes `1e18` as the decimal normalizer throughout its core token-to-rsETH conversion and total-ETH-in-protocol accounting logic. This assumption is only valid for 18-decimal tokens. If any non-18 decimal token (e.g., WBTC with 8 decimals, USDC with 6 decimals) is added as a supported asset — a legitimate admin action the protocol explicitly supports — the rsETH price calculation, rsETH minting amounts, and L2 pool swap amounts will all be catastrophically wrong, leading to protocol insolvency and direct fund loss.

---

### Finding Description

**Root Cause 1 — `LRTOracle._getTotalEthInProtocol()` (line 343):**

```solidity
// assetER is in 1e18 precision (1.0 = 1e18)
uint256 assetER = getAssetPrice(asset);
// totalAssetAmt is in 1e18 precision (standard token decimals)  ← WRONG ASSUMPTION
uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

totalETHInProtocol += totalAssetAmt.mulWad(assetER);  // mulWad divides by 1e18
```

`mulWad` computes `totalAssetAmt * assetER / 1e18`. For an 18-decimal token this is correct. For a 6-decimal token (USDC), `totalAssetAmt` is in 6-decimal units, so the result is `10^12` times too small. This directly corrupts `rsETHPrice`, which is used for all subsequent minting.

**Root Cause 2 — `LRTDepositPool.getRsETHAmountToMint()` (line 520):**

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`amount` is in the asset's native decimals. `getAssetPrice` and `rsETHPrice` are both in 1e18 precision. For a 6-decimal token, the result is in 6-decimal units, but rsETH has 18 decimals — the user receives `10^12` times fewer rsETH than they should.

**Root Cause 3 — `LRTDepositPool.getSwapETHToAssetReturnAmount()` (line 539–541):**

```solidity
uint256 ethPricePerUint = 1e18;
return ethPricePerUint * ethAmountToSend / lrtOracle.getAssetPrice(toAsset);
```

For a 6-decimal `toAsset`, the return amount is in 18-decimal units instead of 6-decimal units — `10^12` times too large, draining the pool.

**Root Cause 4 — L2 Pool `viewSwapRsETHAmountAndFee(amount, token)` (e.g., `RSETHPoolV3.sol` line 334):**

```solidity
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

`amountAfterFee` is in the token's native decimals. `tokenToETHRate` and `rsETHToETHrate` are both in 1e18 precision. For a 6-decimal token, `rsETHAmount` is `10^12` times too small.

**Root Cause 5 — L2 Pool `viewSwapAssetToPremintedRsETH(token, rsETHAmount)` (e.g., `RSETHPoolV3.sol` line 400):**

```solidity
tokenAmount = rsETHAmount * rsETHToETHrate / tokenToETHRate;
```

`rsETHAmount` is in 18-decimal units. For a 6-decimal output token, `tokenAmount` is `10^12` times too large — the pool is drained.

---

### Impact Explanation

**Protocol Insolvency (Critical):** If a non-18 decimal token is added to the L1 protocol, `_getTotalEthInProtocol()` returns a value `10^(18-decimals)` times too small. This makes `rsETHPrice` collapse toward zero, causing all subsequent depositors to mint astronomically large amounts of rsETH for tiny deposits, draining the protocol.

**Direct Fund Theft / Loss (Critical):** A depositor of a non-18 decimal token in `LRTDepositPool.depositAsset()` receives `10^(18-decimals)` times fewer rsETH than their deposit is worth. Conversely, `getSwapETHToAssetReturnAmount()` returns `10^(18-decimals)` times more tokens than it should, enabling fund extraction.

**L2 Pool Fund Drain (Critical):** In `RSETHPoolV3` / `RSETHPoolV3ExternalBridge` / `RSETHPoolV3WithNativeChainBridge`, the reverse swap `viewSwapAssetToPremintedRsETH` returns `10^(18-decimals)` times more tokens than correct, allowing any caller of `swapAssetToPremintedRsETH` (OPERATOR_ROLE) to drain the pool.

---

### Likelihood Explanation

The protocol explicitly supports adding new assets via `LRTConfig.addNewSupportedAsset()` (TIME_LOCK_ROLE) and new tokens to L2 pools via `addSupportedToken` (DEFAULT_ADMIN_ROLE). Neither function enforces an 18-decimal requirement. The oracle validation in `updatePriceOracleForValidated` only checks that the price is between `1e16` and `1e19` — it does not check token decimals. On L2 chains where these pools are deployed (Arbitrum, Base, etc.), WBTC (8 decimals) and USDC (6 decimals) are extremely common assets that a protocol operator might legitimately add. The admin need not be malicious — they simply may not be aware of the decimal assumption embedded in the arithmetic.

---

### Recommendation

Normalize all token amounts to 18-decimal precision before performing arithmetic. Introduce a helper:

```solidity
function _normalizeToWad(uint256 amount, address token) internal view returns (uint256) {
    uint8 decimals = IERC20Metadata(token).decimals();
    if (decimals < 18) return amount * 10 ** (18 - decimals);
    if (decimals > 18) return amount / 10 ** (decimals - 18);
    return amount;
}
```

Apply this normalization in:
- `LRTOracle._getTotalEthInProtocol()` before `mulWad`
- `LRTDepositPool.getRsETHAmountToMint()` before the division
- `LRTDepositPool.getSwapETHToAssetReturnAmount()` / `getSwapAssetForETHReturnAmount()` for the return value
- All L2 pool `viewSwapRsETHAmountAndFee(amount, token)` and `viewSwapAssetToPremintedRsETH(token, rsETHAmount)` functions

Alternatively, enforce at the asset-addition layer that only 18-decimal tokens can be added.

---

### Proof of Concept

**Scenario: WBTC (8 decimals) added to L1 protocol**

1. Admin calls `addNewSupportedAsset(WBTC, depositLimit)` and sets a WBTC price oracle returning `~20e18` (20 ETH/WBTC in 1e18 precision).
2. User deposits 1 WBTC = `1e8` units via `depositAsset(WBTC, 1e8, 0, "")`.
3. `getRsETHAmountToMint(WBTC, 1e8)`:
   - `assetPrice` = `20e18`
   - `rsETHPrice` ≈ `1.05e18`
   - `rsethAmountToMint` = `1e8 * 20e18 / 1.05e18` ≈ `1.9e9`
   - **Correct value**: 1 WBTC × 20 ETH × (1/1.05) rsETH/ETH = ~19 rsETH = `19e18` units
   - **Actual minted**: `1.9e9` units — `10^10` times too little. User loses ~$1.9M of value.
4. `_getTotalEthInProtocol()` after deposit:
   - `totalAssetAmt` = `1e8`
   - `totalETHInProtocol` += `1e8 * 20e18 / 1e18` = `2e9` (wei)
   - **Correct**: 20 ETH = `20e18` wei
   - **Actual**: `2e9` wei — `10^10` times too small, collapsing `rsETHPrice`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/LRTOracle.sol (L336-348)
```text
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

**File:** contracts/LRTDepositPool.sol (L536-561)
```text
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        uint256 ethPricePerUint = 1e18;

        return ethPricePerUint * ethAmountToSend / lrtOracle.getAssetPrice(toAsset);
    }

    /// @notice get return amount for swapping asset to ETH that is accepted by LRTDepositPool
    /// @dev use LRTOracle to get price for fromAsset
    /// @param fromAsset Asset address to swap from
    /// @param fromAssetAmount Asset amount to swap from
    /// @return returnAmount Return amount of ETH
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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L433-455)
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

    /**
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L513-532)
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
