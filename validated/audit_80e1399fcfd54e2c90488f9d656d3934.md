### Title
Token Decimal Miscalculation in `viewSwapRsETHAmountAndFee` Leads to Near-Zero wrsETH Minting for Non-18 Decimal Tokens - (File: contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPoolV3WithNativeChainBridge.sol)

---

### Summary

`RSETHPoolV3` and `RSETHPoolV3WithNativeChainBridge` both expose a `deposit(address token, uint256 amount, string referralId)` path for non-ETH ERC-20 tokens. The internal `viewSwapRsETHAmountAndFee(uint256 amount, address token)` function computes the wrsETH amount to mint without normalizing `amount` to 18-decimal precision, producing a result that is `10^(18 - tokenDecimals)` times too small for any token whose decimals differ from 18.

---

### Finding Description

The ETH deposit path correctly normalizes the input:

```solidity
// RSETHPoolV3.sol L307
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

`amountAfterFee` is already in wei (1e18 precision), and the explicit `* 1e18` keeps the result in 1e18 precision.

The non-ETH token path omits this normalization:

```solidity
// RSETHPoolV3.sol L334
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

`tokenToETHRate` (from `IOracle.getRate()`) is the price of **one full token** expressed in 1e18 ETH precision (e.g., 1 USDC ≈ 4×10¹⁴ wei). `rsETHToETHrate` is similarly 1e18-scaled. When `amountAfterFee` is in the token's native decimals (e.g., 1e6 for USDC), the formula produces:

```
rsETHAmount = (1e6) * (4e14) / (1.05e18) ≈ 380 wei
```

The correct result is:

```
rsETHAmount = (1e6 * 1e12) * (4e14) / (1.05e18) ≈ 3.81e14 wei
```

The missing factor is `10^(18 − tokenDecimals)`. For a 6-decimal token the minted amount is **10¹² times too small**; for an 8-decimal token it is **10¹⁰ times too small**.

The identical bug exists in `RSETHPoolV3WithNativeChainBridge.viewSwapRsETHAmountAndFee`:

```solidity
// RSETHPoolV3WithNativeChainBridge.sol L370
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

The `limitDailyMint` modifier in both contracts calls `viewSwapRsETHAmountAndFee` to track the daily cap, so the cap is also effectively bypassed for non-18 decimal tokens (the computed rsETH amount is negligible, never triggering `DailyMintLimitExceeded`). [1](#0-0) [2](#0-1) [3](#0-2) 

---

### Impact Explanation

A user who calls `deposit(token, amount, referralId)` with a non-18 decimal token (e.g., USDC, WBTC) transfers their full token balance to the pool but receives a near-zero amount of wrsETH. Because there is no user-accessible withdrawal or redemption path in either pool contract, the deposited tokens are permanently inaccessible to the user. This constitutes **permanent freezing of user funds** (Critical). [4](#0-3) [5](#0-4) 

---

### Likelihood Explanation

The `addSupportedToken` admin function in both contracts accepts any ERC-20 address and oracle pair with no decimal restriction. Both pools are deployed on L2 chains where non-18 decimal tokens (USDC = 6 decimals, WBTC = 8 decimals) are standard bridged assets and natural candidates for inclusion. Any unprivileged depositor who calls `deposit` after such a token is listed triggers the loss immediately with no further preconditions. [6](#0-5) 

---

### Recommendation

Normalize `amountAfterFee` to 18-decimal precision before applying the rate formula, mirroring the ETH path:

```solidity
import { IERC20Metadata } from "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";

uint8 tokenDecimals = IERC20Metadata(token).decimals();
uint256 normalizedAmount = amountAfterFee * 10 ** (18 - tokenDecimals);
rsETHAmount = normalizedAmount * tokenToETHRate / rsETHToETHrate;
```

Apply the same fix to `viewSwapAssetToPremintedRsETH` (reverse direction) and to the identical code in `RSETHPoolV3WithNativeChainBridge`. [7](#0-6) [8](#0-7) 

---

### Proof of Concept

**Setup:** USDC (6 decimals) is added as a supported token with an oracle returning `4e14` (≈ 0.0004 ETH per USDC). rsETH oracle returns `1.05e18`.

**Attacker/user calls:**
```solidity
pool.deposit(USDC, 1_000e6, "ref"); // deposits 1,000 USDC
```

**Execution trace:**
```
amountAfterFee = 1_000e6 (assuming 0 fee)
tokenToETHRate = 4e14
rsETHToETHrate = 1.05e18

rsETHAmount = 1_000e6 * 4e14 / 1.05e18
            = 4e23 / 1.05e18
            ≈ 380_952 wei  (~0.000000000000381 wrsETH)
```

**Expected:**
```
normalizedAmount = 1_000e6 * 1e12 = 1_000e18
rsETHAmount = 1_000e18 * 4e14 / 1.05e18 ≈ 380.95e18 wrsETH
```

The user receives `≈ 381,000 wei` of wrsETH instead of `≈ 380.95e18 wei` — a factor of `10^12` shortfall. The 1,000 USDC deposited is permanently locked in the pool with no user-accessible recovery path. [9](#0-8) [10](#0-9)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L81-84)
```text
    modifier onlySupportedToken(address token) {
        if (supportedTokenOracle[token] == address(0)) revert UnsupportedToken();
        _;
    }
```

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

**File:** contracts/pools/RSETHPoolV3.sol (L299-308)
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

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L307-329)
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

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L416-431)
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
```
