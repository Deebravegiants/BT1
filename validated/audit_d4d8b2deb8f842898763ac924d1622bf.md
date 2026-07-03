### Title
Oracle Rate Double-Read Between `limitDailyMint` Modifier and Deposit Body Allows Daily Mint Limit Bypass and Over-Minting via Token Transfer Callback - (File: contracts/pools/RSETHPoolV3.sol)

---

### Summary

The `limitDailyMint` modifier in `RSETHPoolV3` (and identical variants) reads the oracle rate to calculate and record the expected rsETH mint amount for daily-limit enforcement **before** the token transfer. The function body then reads the oracle rate a **second time** after the `safeTransferFrom`. If a supported token has a transfer-time callback (e.g., ERC777 `tokensToSend`), an attacker can manipulate the oracle rate between these two reads, causing the actual minted amount to exceed what was accounted in the daily limit and to exceed the fair exchange rate — directly diluting all other rsETH holders.

---

### Finding Description

In `RSETHPoolV3.deposit(address token, uint256 amount, string referralId)`, Solidity modifiers execute before the function body. The execution order is:

**Phase 1 — `limitDailyMint` modifier** (lines 96–125): [1](#0-0) 

```
(rsETHAmount,) = viewSwapRsETHAmountAndFee(amount, token);   // reads rate R1
...
if (dailyMintAmount + rsETHAmount > dailyMintLimit) revert;  // limit check at R1
dailyMintAmount += rsETHAmount;                              // records amount_1
```

**Phase 2 — function body** (lines 271–293): [2](#0-1) 

```
IERC20(token).safeTransferFrom(msg.sender, address(this), amount); // ← callback window
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token); // reads rate R2
wrsETH.mint(msg.sender, rsETHAmount);                              // mints amount_2
```

The oracle rate is read at R1 in the modifier and at R2 in the body. If a supported token has a transfer hook (ERC777 `tokensToSend`, or any custom `_beforeTokenTransfer`/`_afterTokenTransfer` override), the attacker can call into an external contract during the transfer to manipulate the oracle's underlying price source (e.g., an AMM spot price) to R2 < R1. Because `nonReentrant` only blocks re-entry into the **same** pool contract, calls to external contracts (oracle, AMM, flash-loan provider) are unrestricted.

Result:
- `amount_2 = amount × tokenRate / R2 > amount_1 = amount × tokenRate / R1`
- The daily limit was checked and debited against `amount_1`, but `amount_2` is actually minted.
- The attacker receives more rsETH per deposited token than the protocol intends, diluting all existing rsETH holders.

The same double-read pattern exists identically in:
- `RSETHPoolV3ExternalBridge.deposit(address,uint256,string)` [3](#0-2) 
- `RSETHPoolV3WithNativeChainBridge.deposit(address,uint256,string)` [4](#0-3) 
- `RSETHPool.deposit(address,uint256,string)` [5](#0-4) 
- `RSETHPoolNoWrapper.deposit(address,uint256,string)` [6](#0-5) 

By contrast, `LRTDepositPool.depositAsset` correctly pre-calculates `rsethAmountToMint` once before the transfer and uses that fixed value for minting, avoiding the double-read entirely: [7](#0-6) 

---

### Impact Explanation

**High — Theft of unclaimed yield / value from existing rsETH holders.**

If the oracle rate is driven lower during the callback window, the attacker receives more rsETH per unit of deposited collateral than the protocol's exchange rate warrants. Every extra rsETH minted at a below-market rate dilutes the backing of all existing rsETH holders, transferring value from them to the attacker. Additionally, the daily mint limit — the protocol's primary circuit-breaker against runaway minting — is bypassed: the limit is debited by `amount_1` but `amount_2 > amount_1` is actually minted.

---

### Likelihood Explanation

**Medium.** Two conditions must hold simultaneously:

1. A supported token must have a transfer-time callback. The admin can add arbitrary tokens via `addSupportedToken`. ERC777 tokens, tokens with `_beforeTokenTransfer`/`_afterTokenTransfer` hooks, or rebasing tokens with notify callbacks all qualify. The current default set (stETH, ETHx, rETH, sfrxETH) are standard ERC20 without callbacks, but the token list is admin-extensible.

2. The oracle backing `supportedTokenOracle[token]` or `rsETHOracle` must read a manipulable price source (e.g., an AMM spot price rather than a Chainlink TWAP). The `IOracle.getRate()` interface is generic and the oracle address is admin-configurable per token. [8](#0-7) 

Both conditions are realistic for tokens that may be added in future upgrades.

---

### Recommendation

Pre-calculate the rsETH amount **once** before the token transfer and reuse that value for both the daily-limit accounting and the actual mint — exactly as `LRTDepositPool.depositAsset` already does. Concretely, remove the `viewSwapRsETHAmountAndFee` call from the function body and instead pass the pre-computed value from the modifier (or from a local variable set before `safeTransferFrom`):

```solidity
function deposit(address token, uint256 amount, string memory referralId)
    external nonReentrant whenNotPaused onlySupportedToken(token)
{
    if (amount == 0) revert InvalidAmount();

    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

    _enforceDailyMintLimit(rsETHAmount);          // check + debit with the same value

    IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

    feeEarnedInToken[token] += fee;
    wrsETH.mint(msg.sender, rsETHAmount);         // mint the same pre-computed value
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
}
```

This ensures the rate is read exactly once, before any external call, and the same value is used for limit enforcement and minting.

---

### Proof of Concept

1. Attacker deploys a malicious ERC777 token `MalToken` with a `tokensToSend` hook. Admin adds `MalToken` as a supported token with an AMM-backed oracle.
2. Attacker pre-positions a flash-loan to be ready to drain the AMM pool backing the oracle.
3. Attacker calls `RSETHPoolV3.deposit(MalToken, amount, "")`.
4. **Modifier `limitDailyMint`** executes: oracle reads AMM at normal rate R1 → computes `rsETHAmount_1` → daily limit check passes → `dailyMintAmount += rsETHAmount_1`.
5. **Function body**: `safeTransferFrom` triggers `MalToken.tokensToSend` callback on attacker's contract.
6. Inside the callback, attacker executes the flash loan, draining the AMM to push the oracle rate to R2 ≪ R1, then returns.
7. **Function body continues**: `viewSwapRsETHAmountAndFee` reads R2 → computes `rsETHAmount_2 = amount × tokenRate / R2 ≫ rsETHAmount_1`.
8. `wrsETH.mint(attacker, rsETHAmount_2)` — attacker receives far more rsETH than the daily limit or fair rate permits.
9. Attacker repays flash loan and sells excess rsETH, extracting value from all existing rsETH holders.

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L96-125)
```text
    modifier limitDailyMint(uint256 amount, address token) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }

        uint256 rsETHAmount;

        // Calculate the amount of rsETH that will be minted
        if (token == ETH_IDENTIFIER) {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount);
        } else {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount, token);
        }

        uint256 currentDay = getCurrentDay();

        // If the current day is greater than the last mint day, reset the daily mint amount
        if (currentDay > lastMintDay) {
            lastMintDay = currentDay;
            dailyMintAmount = 0;
        }

        // Check if the daily mint amount plus the amount to mint is greater than the daily mint limit
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L390-412)
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

**File:** contracts/pools/RSETHPool.sol (L284-305)
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
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId); // Add token address?
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L250-271)
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
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId); // Add token address?
    }
```

**File:** contracts/LRTDepositPool.sol (L110-115)
```text
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);
```
