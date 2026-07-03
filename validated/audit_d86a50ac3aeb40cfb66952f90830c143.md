### Title
Global Daily Mint Limit Can Be Exhausted by Any Depositor to Temporarily Block All L2 Pool Deposits - (File: contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPoolV3ExternalBridge.sol, contracts/pools/RSETHPoolV3WithNativeChainBridge.sol)

### Summary
The `limitDailyMint` modifier in all three L2 pool variants maintains a single global `dailyMintAmount` counter shared across every depositor. Any unprivileged user can call `deposit()` with enough ETH or supported tokens to exhaust the entire daily quota, causing every subsequent deposit by any other user to revert with `DailyMintLimitExceeded` for up to 24 hours. The attacker receives wrsETH in return, making the attack economically self-funding and repeatable every day.

### Finding Description
The `limitDailyMint` modifier is applied to both `deposit(string)` (ETH) and `deposit(address,uint256,string)` (token) in `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, and `RSETHPoolV3WithNativeChainBridge`. The modifier reads and writes a single contract-level `dailyMintAmount` variable:

```solidity
// RSETHPoolV3.sol lines 119-123
if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
    revert DailyMintLimitExceeded();
}
dailyMintAmount += rsETHAmount;
```

There is no per-user sub-limit or per-user accounting. The entire `dailyMintLimit` is a shared pool. Once `dailyMintAmount` reaches `dailyMintLimit`, every call to `deposit()` from any address reverts until the next calendar day resets the counter:

```solidity
// RSETHPoolV3.sol lines 113-116
if (currentDay > lastMintDay) {
    lastMintDay = currentDay;
    dailyMintAmount = 0;
}
```

The attacker deposits exactly `remainingDailyMintLimit()` worth of ETH or tokens in one or a few transactions, receives wrsETH proportionally, and leaves the pool's daily quota at zero. All other users are blocked for the remainder of the day. The attack costs only gas and temporary capital lockup; the attacker holds wrsETH and can reverse-swap or hold it.

### Impact Explanation
**Medium — Temporary freezing of funds.**

All L2 users are unable to deposit ETH or supported LSTs into the pool for up to 24 hours per attack cycle. The attacker can repeat this every day at the start of each new day, creating a sustained denial-of-service against the deposit path. Users who need to enter the protocol on L2 (to obtain wrsETH for DeFi use, yield, or bridging) are blocked. The freeze is temporary (resets daily) but is repeatable indefinitely at low cost.

### Likelihood Explanation
**Medium.**

The attack requires only a single `deposit()` call with sufficient capital to exhaust the remaining daily limit. The attacker receives wrsETH in return, so the net capital cost is near zero (only gas). The `remainingDailyMintLimit()` view function is public, making it trivial to calculate the exact amount needed. The attack is repeatable every 24 hours. Any actor with sufficient ETH or supported tokens on the L2 can execute this.

### Recommendation
Replace the single global `dailyMintAmount` counter with per-user sub-limits, or introduce a maximum per-transaction deposit cap that prevents any single depositor from consuming the entire daily quota. Alternatively, implement a per-address cooldown or rate limit so that no single address can exhaust more than a defined fraction of the daily limit. At minimum, document the griefing risk and set the `dailyMintLimit` high enough that exhausting it requires capital that makes the attack economically irrational.

### Proof of Concept

1. The daily limit is set to `D` rsETH-equivalent (e.g., 100 ETH worth of wrsETH).
2. At the start of a new day, `dailyMintAmount` resets to 0.
3. Attacker calls `RSETHPoolV3.deposit{value: X}("")` where `X` is chosen so that `viewSwapRsETHAmountAndFee(X).rsETHAmount == D`. The `limitDailyMint` modifier sets `dailyMintAmount = D`.
4. Alice calls `RSETHPoolV3.deposit{value: 1 ether}("")`. The modifier computes `dailyMintAmount + rsETHAmount > dailyMintLimit` → `true` → reverts with `DailyMintLimitExceeded`.
5. All other users are blocked until `block.timestamp / 1 days` increments, resetting `dailyMintAmount` to 0.
6. Attacker repeats step 3 at the start of the next day.

Relevant code paths: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L364-380)
```text
    /// @dev Swaps ETH for rsETH
    /// @param referralId The referral id
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

```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L108-137)
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

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L282-301)
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
