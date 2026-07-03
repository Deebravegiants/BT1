### Title
Block Stuffing Delays `InterimRSETHOracle` Rate Update, Exhausting `dailyMintLimit` Faster Than Intended — (`contracts/pools/oracle/InterimRSETHOracle.sol`, `contracts/pools/RSETHPoolV3.sol`)

---

### Summary

An attacker can fill blocks with high-gas-price transactions to prevent the `MANAGER_ROLE` holder from calling `InterimRSETHOracle.setRate()`. While the oracle is stuck at a stale (lower) rate, every ETH deposit mints more rsETH than it should, exhausting `dailyMintLimit` faster than intended and denying service to legitimate depositors for the remainder of the day.

---

### Finding Description

`InterimRSETHOracle` stores the rsETH/ETH rate as a plain storage variable with no on-chain freshness enforcement: [1](#0-0) 

The rate is updated only when a `MANAGER_ROLE` account submits a `setRate()` transaction. If that transaction is excluded from blocks (via block stuffing), the oracle remains at `stale_rate`.

`RSETHPoolV3.viewSwapRsETHAmountAndFee` computes the rsETH amount as:

```
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate
``` [2](#0-1) 

The `limitDailyMint` modifier accumulates this `rsETHAmount` against `dailyMintLimit`: [3](#0-2) 

Because the divisor is `stale_rate < new_rate`, each deposit produces a larger `rsETHAmount`, consuming the daily cap faster. For example:

| Rate | ETH deposited to hit N rsETH cap |
|---|---|
| `stale_rate = 1e18` | N ETH |
| `new_rate = 1.05e18` | 1.05 × N ETH |

The attacker stuffs blocks only long enough to prevent the single `setRate()` call, then stops. The damage (exhausted daily cap) persists until midnight UTC resets `dailyMintAmount`.

---

### Impact Explanation

Legitimate depositors receive `DailyMintLimitExceeded` reverts for the rest of the day. The protocol fails to deliver its promised deposit service at the correct exchange rate. No funds are lost, but the daily deposit window is effectively stolen. This matches **Low. Block stuffing** and **Low. Contract fails to deliver promised returns, but doesn't lose value**.

---

### Likelihood Explanation

- `InterimRSETHOracle` is explicitly described as a manually-operated interim oracle; rate updates are infrequent and predictable (e.g., daily or after staking rewards accrue), making the timing of the `setRate()` transaction observable.
- Block stuffing is cheapest on low-throughput or low-fee chains (L2s, testnets) where this interim oracle is most likely deployed during early phases.
- The attacker needs to stuff blocks only for the duration of the manager's retry window (seconds to minutes), not indefinitely.
- No privileged key compromise is required; the attacker only needs to outbid the manager's gas price.

---

### Recommendation

1. **Add a staleness deadline to `InterimRSETHOracle`**: record `lastUpdated = block.timestamp` in `_setRate` and revert in `getRate()` if `block.timestamp - lastUpdated > MAX_STALENESS`.
2. **Cap rsETH minted per deposit in `limitDailyMint`** using the *higher* of the current rate and a floor, so a stale low rate cannot inflate the rsETH amount beyond a safe bound.
3. **Use a time-weighted or commit-reveal rate update** so the effective rate cannot be manipulated by delaying a single transaction.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.27;

// Scenario (local fork or unit test, no mainnet):
// 1. Deploy InterimRSETHOracle(admin, 1e18)  → stale_rate = 1e18
// 2. Deploy RSETHPoolV3, set dailyMintLimit = 100e18 (100 rsETH)
// 3. Attacker stuffs blocks → manager's setRate(1.05e18) never lands
// 4. At stale_rate=1e18: deposit(100 ETH) → rsETHAmount = 100e18 → limit hit
// 5. At new_rate=1.05e18: deposit(100 ETH) → rsETHAmount ≈ 95.24e18 → limit NOT hit
//    → need ~105 ETH to hit the same 100 rsETH cap

function testBlockStuffingExhaustsDailyLimit() public {
    // stale rate: 1 ETH = 1 rsETH
    oracle.setRate(1e18);
    pool.setDailyMintLimit(100e18);

    // Deposit 100 ETH at stale rate → mints 100 rsETH → limit exhausted
    vm.deal(attacker, 100 ether);
    vm.prank(attacker);
    pool.deposit{value: 100 ether}("ref");

    // Legitimate user cannot deposit even 1 wei more
    vm.deal(user, 1 ether);
    vm.prank(user);
    vm.expectRevert(RSETHPoolV3.DailyMintLimitExceeded.selector);
    pool.deposit{value: 1 ether}("ref");

    // If rate had been updated to 1.05e18, 100 ETH would only mint ~95.24 rsETH
    // → user's 1 ETH deposit would succeed (95.24 + 0.952 < 100)
}
``` [4](#0-3) [5](#0-4)

### Citations

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
