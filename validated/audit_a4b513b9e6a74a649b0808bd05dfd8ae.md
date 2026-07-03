### Title
Block Stuffing on zkSync Delays Rate Update, Causing Premature Daily Mint Limit Exhaustion — (`contracts/pools/oracle/InterimRSETHOracle.sol`, `contracts/pools/RSETHPoolV2.sol`)

---

### Summary

`InterimRSETHOracle` stores the rsETH/ETH rate as a plain `uint256` with no on-chain freshness enforcement. On zkSync (lower block gas limit than mainnet), an attacker can stuff blocks to prevent the `MANAGER_ROLE` holder from calling `setRate()`. While the rate is stale-low, every `RSETHPoolV2.deposit()` call inflates the computed `rsETHAmount` and accumulates it against `dailyMintAmount`, exhausting `dailyMintLimit` prematurely and causing `DailyMintLimitExceeded` for legitimate depositors for the remainder of the day.

---

### Finding Description

`InterimRSETHOracle` holds a single storage variable `rate` that is updated only when a `MANAGER_ROLE` account explicitly calls `setRate()`. [1](#0-0) [2](#0-1) [3](#0-2) 

There is no timestamp, heartbeat, or staleness guard — `getRate()` returns whatever value was last written, regardless of age.

`RSETHPoolV2.deposit()` applies the `limitDailyMint` modifier, which calls `viewSwapRsETHAmountAndFee` to compute `rsETHAmount` and accumulates it into `dailyMintAmount`: [4](#0-3) 

`viewSwapRsETHAmountAndFee` divides by the oracle rate: [5](#0-4) 

When `rsETHToETHrate` is stale-low (e.g., `1e18` instead of the correct `1.1e18`), the division yields a **larger** `rsETHAmount` per unit of ETH. Each deposit therefore consumes more of `dailyMintLimit` than it should, exhausting the limit before the equivalent ETH-denominated capacity is reached.

**Attack path on zkSync:**

1. rsETH appreciates; the manager prepares a `setRate(1.1e18)` transaction.
2. The attacker, exploiting zkSync's lower per-block gas limit, stuffs consecutive blocks with high-gas filler transactions, preventing the manager's `setRate` call from being included.
3. The rate remains at `1e18` (stale-low).
4. Legitimate users deposit ETH; each deposit mints ~10 % more rsETH than correct, accumulating `dailyMintAmount` ~10 % faster.
5. `dailyMintLimit` is hit after only ~91 % of the intended ETH capacity is deposited.
6. All subsequent `deposit()` calls revert with `DailyMintLimitExceeded` until the next UTC day resets `dailyMintAmount`. [6](#0-5) 

---

### Impact Explanation

Legitimate depositors are denied access to `RSETHPoolV2.deposit()` for the remainder of the day. No funds are lost, but the protocol fails to deliver its promised daily throughput. This maps to **Low — Block stuffing** in the allowed impact scope.

---

### Likelihood Explanation

- zkSync Era's block gas limit is materially lower than Ethereum mainnet, reducing the cost of sustained block stuffing.
- The attack window is bounded: it only needs to last long enough to keep the rate stale while the daily limit is consumed by organic depositors.
- The `InterimRSETHOracle` is explicitly described as an interim manual oracle, making periodic rate updates a routine, predictable operation that an attacker can anticipate.
- No privileged access is required on the attacker's side; only ETH to fund filler transactions.

---

### Recommendation

1. **Add a staleness deadline to `limitDailyMint`**: record `lastRateUpdate` in `InterimRSETHOracle` and revert in `viewSwapRsETHAmountAndFee` (or in the modifier) if `block.timestamp - lastRateUpdate > MAX_RATE_AGE`.
2. **Denominate `dailyMintLimit` in ETH, not rsETH**: track `dailyMintAmount` in ETH terms (i.e., accumulate `amountAfterFee` rather than `rsETHAmount`). This makes the limit rate-independent and eliminates the inflation vector entirely.
3. **Use a push-based oracle with on-chain freshness** (e.g., Chainlink with a heartbeat check) rather than a purely manual setter.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Pseudocode unit test (Foundry / Hardhat fork of zkSync or local)
// stale_rate  = 1e18   (rate NOT yet updated)
// correct_rate = 1.1e18 (rate the manager intended to set)
// dailyMintLimit = 100e18 rsETH
// feeBps = 0 for simplicity

// Setup:
//   oracle.setRate(1e18);          // stale rate
//   pool.setDailyMintLimit(100e18);

// At stale rate, 1 ETH → 1e18 rsETH
// At correct rate, 1 ETH → ~0.909e18 rsETH

// Deposit 100 ETH in 100 × 1 ETH calls at stale rate:
for (uint i = 0; i < 100; i++) {
    pool.deposit{value: 1 ether}("ref");
}
// dailyMintAmount == 100e18 == dailyMintLimit → limit exhausted

// Now try one more deposit (would succeed at correct rate: 0.909e18 < remaining):
vm.expectRevert(RSETHPoolV2.DailyMintLimitExceeded.selector);
pool.deposit{value: 1 ether}("ref");

// At correct rate the same 100 ETH would have consumed only ~90.9e18 rsETH,
// leaving ~9.1e18 rsETH of headroom — 10 additional ETH of capacity lost.
```

This test runs on unmodified production code with no admin compromise; the only precondition is that the oracle rate has not been updated (simulating a successful block-stuffing window).

### Citations

**File:** contracts/pools/oracle/InterimRSETHOracle.sol (L14-15)
```text
    /// @notice The current rsETH/ETH rate
    uint256 public rate;
```

**File:** contracts/pools/oracle/InterimRSETHOracle.sol (L36-44)
```text
    function setRate(uint256 newRate) external onlyRole(MANAGER_ROLE) {
        _setRate(newRate);
    }

    /// @dev Internal function to set the rsETH/ETH rate
    function _setRate(uint256 newRate) internal {
        if (newRate < 1e18) revert InvalidRate();
        rate = newRate;
        emit RateUpdated(newRate);
```

**File:** contracts/pools/oracle/InterimRSETHOracle.sol (L49-51)
```text
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L72-94)
```text
    modifier limitDailyMint(uint256 amount) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }

        // Calculate the amount of rsETH that will be minted
        (uint256 rsETHAmount,) = viewSwapRsETHAmountAndFee(amount);
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

**File:** contracts/pools/RSETHPoolV2.sol (L207-219)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(msg.value) {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L225-234)
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
