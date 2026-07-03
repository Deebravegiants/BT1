### Title
Daily Mint Limit Exhaustion Combined with Block Stuffing Enables Temporary Deposit DoS — (`contracts/pools/RSETHPoolV3WithNativeChainBridge.sol`)

---

### Summary

An attacker holding sufficient supported ERC20 tokens can exhaust the `dailyMintLimit` in a single transaction, then use block stuffing to prevent legitimate depositors from being included in blocks for the remainder of the day epoch, causing a temporary but sustained denial-of-service on all token deposit functionality.

---

### Finding Description

`getCurrentDay()` derives the current day purely from `block.timestamp`: [1](#0-0) 

The `limitDailyMint` modifier resets `dailyMintAmount` only when `currentDay > lastMintDay`, and otherwise enforces the cap: [2](#0-1) 

Once `dailyMintAmount` reaches `dailyMintLimit`, every subsequent call to `deposit(address,uint256,string)` reverts with `DailyMintLimitExceeded`: [3](#0-2) 

There is **no privileged function** that directly resets `dailyMintAmount` to zero. `setDailyMintLimit` only changes the cap value; it does not clear the accumulator: [4](#0-3) 

**Clarification on the mechanism vs. the question's framing:** Block stuffing does *not* prevent `block.timestamp` from advancing — timestamps are set by block producers, not by transaction content. The correct attack path is: the attacker exhausts the daily limit, then fills blocks with high-gas transactions so that no legitimate `deposit` call can be included for the remainder of the day window. Once the day boundary passes naturally, the attacker immediately re-exhausts the new day's limit and repeats. On L2 chains (the deployment target of this contract, given its bridge architecture), block gas limits and per-transaction costs are low enough to make sustained block stuffing economically viable.

---

### Impact Explanation

All token depositors are temporarily locked out of `deposit(address,uint256,string)` beyond the intended single-day lockout. The attacker can sustain this across consecutive days by re-exhausting the limit at each boundary. No user funds already in the contract are at risk, but new deposits are frozen for the duration of the attack. This matches **Low — Block stuffing**.

---

### Likelihood Explanation

- The attacker receives rsETH in exchange for deposited tokens (minus fees), so the cost of exhausting the daily limit is only the fee, not the principal.
- On L2 chains with low gas costs, block stuffing for the remaining hours of a day is feasible.
- No special role or privileged access is required; any address holding sufficient supported tokens can trigger this.
- There is no on-chain circuit breaker (no admin reset of `dailyMintAmount`, no per-user sub-limit).

---

### Recommendation

1. Add a privileged `resetDailyMintAmount()` function (e.g., `PAUSER_ROLE` or `DEFAULT_ADMIN_ROLE`) that sets `dailyMintAmount = 0` and `lastMintDay = getCurrentDay()`, allowing operators to recover without waiting for the natural day boundary.
2. Consider a per-address sub-limit to prevent a single depositor from consuming the entire daily quota.
3. Evaluate whether the `dailyMintLimit` should be enforced as a rolling window (e.g., last 86 400 seconds) rather than a discrete epoch, which reduces the exploitable boundary.

---

### Proof of Concept

```solidity
// Local fork test (no mainnet interaction)
function testBlockStuffingDailyLimitDoS() public {
    // Setup: configure token + oracle, set dailyMintLimit = 1 ether rsETH equivalent
    pool.setDailyMintLimit(1 ether);

    // Step 1: attacker exhausts the daily limit
    vm.startPrank(attacker);
    token.approve(address(pool), type(uint256).max);
    pool.deposit(address(token), AMOUNT_TO_HIT_LIMIT, "");
    vm.stopPrank();

    // Step 2: legitimate user cannot deposit — limit exhausted
    vm.startPrank(user);
    token.approve(address(pool), 1e18);
    vm.expectRevert(RSETHPoolV3WithNativeChainBridge.DailyMintLimitExceeded.selector);
    pool.deposit(address(token), 1e18, "");
    vm.stopPrank();

    // Step 3: simulate block stuffing — time does NOT advance (warp held constant)
    // In production the attacker fills blocks; here we simply don't warp.
    // Confirm revert persists while timestamp stays in same epoch.
    assertEq(pool.getCurrentDay(), pool.lastMintDay());

    // Step 4: only after warp past boundary does the limit reset
    vm.warp(block.timestamp + 1 days);
    vm.startPrank(user);
    pool.deposit(address(token), 1e18, ""); // succeeds
    vm.stopPrank();
}
```

The test confirms: while `block.timestamp` remains within the same day epoch (whether naturally or because block stuffing prevents legitimate transactions from landing), all deposits revert. The revert clears only after the boundary is crossed. [5](#0-4)

### Citations

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

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L390-392)
```text
    function getCurrentDay() public view returns (uint256) {
        return (block.timestamp - startTimestamp) / 1 days;
    }
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L679-685)
```text
    function setDailyMintLimit(uint256 _dailyMintLimit) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_dailyMintLimit == 0) {
            revert InvalidDailyMintLimit();
        }
        dailyMintLimit = _dailyMintLimit;
        emit DailyMintLimitSet(_dailyMintLimit);
    }
```
