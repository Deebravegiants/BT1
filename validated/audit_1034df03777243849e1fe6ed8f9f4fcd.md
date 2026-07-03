### Title
Attacker Can Exhaust Daily Mint Limit with Dust Deposits to DoS Legitimate Depositors - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
The `limitDailyMint` modifier in `RSETHPoolV3` uses a shared `dailyMintAmount` counter that any depositor can freely increment. An attacker can front-run legitimate large deposits with a dust amount (1 wei) to push `dailyMintAmount` past `dailyMintLimit`, causing the victim's deposit to revert with `DailyMintLimitExceeded` for up to 24 hours — directly analogous to the M-16 pattern where a shared counter is manipulated by a tiny amount to force victim transactions to revert.

### Finding Description
The `limitDailyMint` modifier enforces a global daily cap on rsETH minting:

```solidity
if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
    revert DailyMintLimitExceeded();
}
dailyMintAmount += rsETHAmount;
```

`dailyMintAmount` is a single shared storage slot that every depositor increments. There is no per-user accounting and no mechanism to cap a deposit at the remaining headroom — it is all-or-nothing. An attacker who observes a pending large deposit in the mempool can front-run it with a 1-wei ETH deposit. The resulting rsETH minted from 1 wei is non-zero (due to integer arithmetic at scale), and if `dailyMintAmount` was already close to `dailyMintLimit`, this dust increment is enough to push the sum over the limit. The victim's transaction then reverts. The attacker receives wrsETH for their 1-wei deposit, so their net cost is only gas. They can repeat this indefinitely within the same day, blocking all deposits until the 24-hour window resets.

Both public deposit entry points are affected:
- `deposit(string memory referralId)` (ETH path)
- `deposit(address token, uint256 amount, string memory referralId)` (ERC-20 path) [1](#0-0) [2](#0-1) [3](#0-2) 

### Impact Explanation
All depositors are locked out of the L2 pool for up to 24 hours per attack cycle. Because the attacker recovers their capital as wrsETH, the attack can be sustained at near-zero cost. Users who need to deposit urgently (e.g., to hedge a position or meet a deadline) are unable to do so. This constitutes a **temporary freezing of the deposit path** — matching the "Medium. Temporary freezing of funds" impact tier.

### Likelihood Explanation
The attack requires only mempool visibility and a 1-wei deposit. No special role, no capital at risk, and no complex setup. Any MEV searcher or griefing actor can execute this. The condition (daily limit nearly exhausted) is realistic during high-volume periods, and the attacker can also manufacture it by depositing up to just below the limit themselves before targeting victims.

### Recommendation
Instead of reverting when the deposit would exceed the daily limit, cap the accepted amount to the remaining headroom and refund the excess to the caller. Alternatively, track per-user daily limits so a single actor cannot exhaust the global cap. At minimum, expose a `remainingDailyMintLimit()` view (already present) prominently in the deposit flow so callers can self-limit, and document that deposits near the cap are subject to front-running. [4](#0-3) 

### Proof of Concept

```
Setup:
  dailyMintLimit  = 1_000 ETH-equivalent rsETH
  dailyMintAmount = 999.9 ETH-equivalent rsETH  (naturally consumed by real users)

Step 1 – Victim submits:
  deposit{value: 0.1 ETH}("ref")
  → rsETHAmount ≈ 0.1 ETH-equivalent
  → check: 999.9 + 0.1 = 1000 ≤ 1000  ✓  (would succeed)

Step 2 – Attacker front-runs with:
  deposit{value: 1 wei}("ref")
  → rsETHAmount = tiny but non-zero (e.g., 1 unit at 18-decimal precision)
  → dailyMintAmount becomes 999.9...001

Step 3 – Victim's transaction executes:
  check: 999.9...001 + 0.1 > 1000  → revert DailyMintLimitExceeded

Step 4 – Attacker holds wrsETH worth ~1 wei; net cost = gas only.
         Attacker repeats Step 2 for every retry by the victim.
         Victim is blocked until block.timestamp crosses the next 24-hour boundary.
``` [5](#0-4)

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

**File:** contracts/pools/RSETHPoolV3.sol (L344-350)
```text
    /// @return uint256 The remaining daily minting limit
    function remainingDailyMintLimit() external view returns (uint256) {
        // If we're on a new day but no mint has occurred yet, treat dailyMintAmount as 0
        uint256 effectiveDailyMintAmount = (getCurrentDay() > lastMintDay) ? 0 : dailyMintAmount;

        return dailyMintLimit - effectiveDailyMintAmount;
    }
```
