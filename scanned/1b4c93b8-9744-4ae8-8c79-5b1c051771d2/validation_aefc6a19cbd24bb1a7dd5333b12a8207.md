### Title
Daily Mint Limit Exhaustion Enables Temporary DoS on L2 Deposits - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
Any unprivileged depositor can exhaust the global `dailyMintLimit` in `RSETHPoolV3` by depositing a large amount in a single transaction, preventing all other users from depositing for up to 24 hours. This is a direct structural analog to M-08: a deposit action modifies a shared global counter that gates all other users' access to the same function.

### Finding Description
`RSETHPoolV3` enforces a per-day cap on wrsETH minting via the `limitDailyMint` modifier applied to both `deposit(string)` (ETH) and `deposit(address,uint256,string)` (token):

```solidity
modifier limitDailyMint(uint256 amount, address token) {
    ...
    uint256 currentDay = getCurrentDay();
    if (currentDay > lastMintDay) {
        lastMintDay = currentDay;
        dailyMintAmount = 0;          // resets once per day
    }
    if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
        revert DailyMintLimitExceeded();
    }
    dailyMintAmount += rsETHAmount;   // global counter, shared by all users
    _;
}
```

`dailyMintAmount` is a single global accumulator. There is no per-user sub-limit. Any depositor who submits a transaction that mints exactly `dailyMintLimit - dailyMintAmount` wrsETH atomically exhausts the remaining capacity for the current 24-hour window. Every subsequent deposit call by any other user reverts with `DailyMintLimitExceeded` until `getCurrentDay()` advances past `lastMintDay`.

A malicious actor repeats this once per day (depositing the minimum amount needed to top off the limit) to sustain the DoS indefinitely across consecutive windows. The attacker receives wrsETH in return, so the cost is the opportunity cost of capital, not a direct loss — making the attack economically viable for a well-capitalised adversary.

The parallel to M-08 is exact in structure:
- M-08: `stake()` → resets RocketPool deposit delay → all `unstake()` calls revert.
- Here: `deposit()` → exhausts `dailyMintAmount` → all subsequent `deposit()` calls revert for up to 24 h.

### Impact Explanation
**Low — Contract fails to deliver promised returns, but doesn't lose value.**

Users who attempt to deposit ETH or supported tokens after the daily limit is exhausted receive a revert. Their funds remain in their own wallets (no loss), but the protocol fails to deliver the wrsETH minting service it promises for up to 24 hours per attack cycle. Existing wrsETH holders are unaffected.

### Likelihood Explanation
**Medium.**

The attack requires capital equal to the remaining daily mint capacity in a single block. The `dailyMintLimit` is set by the admin and can be any value; at moderate limits (e.g., a few hundred ETH equivalent), the attack is accessible to any moderately funded actor. No privileged role, oracle manipulation, or external protocol compromise is required — only a standard `deposit()` call.

### Recommendation
Introduce a per-address sub-limit within the daily window (e.g., `maxDepositPerUserPerDay`) so that no single depositor can consume the entire global budget. Alternatively, enforce a minimum deposit cooldown per address to raise the cost of repeated exhaustion attacks.

### Proof of Concept
1. The current `dailyMintLimit` is 500 wrsETH and `dailyMintAmount` is 0 at the start of a new day.
2. Bob (attacker) calls `deposit{value: X}("")` where `X` is chosen so that `viewSwapRsETHAmountAndFee(X)` returns exactly 500 wrsETH. The modifier sets `dailyMintAmount = 500`.
3. Alice calls `deposit{value: 0.1 ether}("")`. The modifier computes `dailyMintAmount + rsETHAmount = 500 + ε > 500 = dailyMintLimit` and reverts with `DailyMintLimitExceeded`.
4. Alice cannot deposit until `getCurrentDay()` increments (up to 24 hours later).
5. Bob repeats step 2 at the start of each new day, sustaining the DoS indefinitely.

Relevant code: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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

**File:** contracts/pools/RSETHPoolV3.sol (L337-350)
```text
    /// @notice Gets the current day relative to the start timestamp
    /// @return uint256 The current day relative to the start timestamp
    function getCurrentDay() public view returns (uint256) {
        return (block.timestamp - startTimestamp) / 1 days;
    }

    /// @notice Gets the remaining daily minting limit
    /// @return uint256 The remaining daily minting limit
    function remainingDailyMintLimit() external view returns (uint256) {
        // If we're on a new day but no mint has occurred yet, treat dailyMintAmount as 0
        uint256 effectiveDailyMintAmount = (getCurrentDay() > lastMintDay) ? 0 : dailyMintAmount;

        return dailyMintLimit - effectiveDailyMintAmount;
    }
```
