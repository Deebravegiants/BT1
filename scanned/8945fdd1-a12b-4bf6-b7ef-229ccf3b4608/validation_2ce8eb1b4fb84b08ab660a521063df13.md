### Title
Shared `dailyMintAmount` Counter Across Independent Deposit Paths Causes Temporary Deposit Freeze - (File: contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPoolV3ExternalBridge.sol)

---

### Summary

In `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, and `RSETHPoolV2ExternalBridge`, a single `dailyMintAmount` counter is shared across all deposit paths — both native ETH deposits and LST token deposits. When one deposit path exhausts the daily limit, all other independent deposit paths are blocked for up to 24 hours. This is the direct analog of the Reserve Protocol issue: a single shared state variable that should be per-subsystem (per-asset) instead of global causes one path's activity to freeze another unrelated path.

---

### Finding Description

The `limitDailyMint` modifier in `RSETHPoolV3.sol` accumulates rsETH minted from **all** deposit types into a single `dailyMintAmount` counter:

```solidity
modifier limitDailyMint(uint256 amount, address token) {
    ...
    if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
        revert DailyMintLimitExceeded();
    }
    dailyMintAmount += rsETHAmount;
    _;
}
```

Both deposit functions apply this same modifier:

- `deposit(string referralId)` — ETH deposits — uses `limitDailyMint(msg.value, ETH_IDENTIFIER)`
- `deposit(address token, uint256 amount, string referralId)` — LST token deposits — uses `limitDailyMint(amount, token)`

ETH and LST tokens are independent assets with independent bridging paths, independent oracles, and independent fee accounting. However, they share a single `dailyMintAmount` counter. When ETH deposits fill `dailyMintLimit`, LST token deposits revert with `DailyMintLimitExceeded`, and vice versa. The block persists until the next 24-hour period resets `dailyMintAmount` to zero.

The same pattern exists in `RSETHPoolV3ExternalBridge.sol` (lines 130–159), `RSETHPoolV3WithNativeChainBridge.sol` (lines 121–136), and `RSETHPoolV2ExternalBridge.sol` (lines 102–126). [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

---

### Impact Explanation

**Medium — Temporary freezing of funds.**

When the shared `dailyMintAmount` counter is exhausted by one deposit path, all other deposit paths are blocked for up to 24 hours. Users who wish to deposit LST tokens (e.g., wstETH) are denied service even though their asset is entirely independent of ETH deposits. Depositors cannot enter the protocol during this window, which means they cannot obtain wrsETH and are denied the yield accrual that would have started from their deposit time. This matches the "Temporary freezing of funds" impact category.

---

### Likelihood Explanation

**Medium.** The daily mint limit is a finite cap. Any combination of organic large ETH deposits — or a single depositor making a large ETH deposit — can exhaust the limit and block LST token depositors for the remainder of the 24-hour window. No special privilege is required; any unprivileged depositor can trigger this condition through normal protocol use. The pools are live on multiple L2 chains, increasing the probability of the limit being hit.

---

### Recommendation

Replace the single shared `dailyMintAmount` / `dailyMintLimit` pair with per-asset counters and limits:

```solidity
mapping(address token => uint256) public dailyMintAmount;
mapping(address token => uint256) public dailyMintLimit;
mapping(address token => uint256) public lastMintDay;
```

This ensures that ETH deposits filling the ETH daily limit do not affect LST token deposit paths, and vice versa — directly mirroring the Reserve Protocol fix of disabling auctions on a per-collateral basis rather than globally.

---

### Proof of Concept

1. The pool is deployed with `dailyMintLimit = 1000 wrsETH` and supports both ETH and wstETH deposits.
2. Alice deposits a large amount of ETH, minting 1000 wrsETH. `dailyMintAmount` is now 1000.
3. Bob attempts to deposit wstETH via `deposit(wstETH, amount, referralId)`.
4. The `limitDailyMint` modifier computes the rsETH equivalent of Bob's wstETH deposit and checks: `dailyMintAmount + rsETHAmount > dailyMintLimit` → `1000 + X > 1000` → reverts with `DailyMintLimitExceeded`.
5. Bob's wstETH deposit is blocked for up to 24 hours, even though his deposit is entirely independent of Alice's ETH deposit.
6. Bob cannot obtain wrsETH during this window and loses the yield accrual that would have started from his intended deposit time. [5](#0-4) [6](#0-5)

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

**File:** contracts/pools/RSETHPoolV3.sol (L246-265)
```text
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
    {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L130-159)
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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L366-412)
```text
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
    {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }

    /// @dev Swaps supported token for rsETH
    /// @param token The token address
    /// @param amount The amount of token
    /// @param referralId The referral id
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
