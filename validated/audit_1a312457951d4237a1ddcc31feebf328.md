### Title
Single Depositor Can Exhaust Daily Mint Limit, Temporarily Freezing All L2 Pool Deposits - (File: contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPoolV3ExternalBridge.sol, contracts/pools/RSETHPoolV3WithNativeChainBridge.sol)

---

### Summary

The `limitDailyMint` modifier enforces a shared per-day cap on wrsETH minting across all depositors, but imposes no per-user sub-limit. A single whale can consume the entire `dailyMintLimit` in one transaction, causing every subsequent `deposit()` call from any other user to revert with `DailyMintLimitExceeded` for up to 24 hours. The attack is repeatable every day at a cost of only the protocol fee, and the attacker retains the wrsETH received.

---

### Finding Description

The `limitDailyMint` modifier is applied to both `deposit(string)` (ETH) and `deposit(address,uint256,string)` (token) in `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, and `RSETHPoolV3WithNativeChainBridge`:

```solidity
// contracts/pools/RSETHPoolV3.sol lines 96-125
modifier limitDailyMint(uint256 amount, address token) {
    ...
    uint256 currentDay = getCurrentDay();
    if (currentDay > lastMintDay) {
        lastMintDay = currentDay;
        dailyMintAmount = 0;
    }
    if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
        revert DailyMintLimitExceeded();
    }
    dailyMintAmount += rsETHAmount;
    _;
}
```

There is no per-depositor cap. The entire `dailyMintLimit` is a single shared bucket. A depositor who sends enough ETH/tokens to produce `rsETHAmount == dailyMintLimit` in one call sets `dailyMintAmount = dailyMintLimit`, and every subsequent deposit that day reverts.

The same modifier with identical logic appears in:
- `contracts/pools/RSETHPoolV3ExternalBridge.sol` lines 130–159
- `contracts/pools/RSETHPoolV3WithNativeChainBridge.sol` lines 108–137

The attacker's only cost is `feeBps` on the deposited amount (up to 10% in `RSETHPoolV3ExternalBridge`, up to 10% in `RSETHPoolV3`). They receive wrsETH in return, which they can hold or sell. The attack can be repeated at the start of every new day.

---

### Impact Explanation

**Medium — Temporary freezing of funds.**

All users on the affected L2 chain are blocked from depositing ETH or supported LSTs into the pool for up to 24 hours per attack cycle. Because the attack is repeatable at the start of each new day, the attacker can sustain the denial of service indefinitely. Users who need to enter the protocol (e.g., to hedge a position, capture a yield opportunity, or respond to market conditions) are unable to do so. The pool's core function — swapping ETH/LSTs for wrsETH — is rendered unavailable to all non-attacker participants.

---

### Likelihood Explanation

**Medium.**

The capital required equals the ETH value corresponding to `dailyMintLimit` wrsETH. The daily limit is set by the admin and is intended to be a meaningful cap, so it is finite and knowable on-chain. A whale or competitor protocol with sufficient capital can execute this in a single transaction. The only recurring cost is the fee on each day's deposit. The attacker retains the wrsETH, so the net cost approaches zero if wrsETH can be sold or redeemed at fair value. No special permissions, oracle manipulation, or governance capture are required — only a public `deposit()` call.

---

### Recommendation

1. **Per-user daily sub-limit**: Track `dailyMintAmountPerUser[msg.sender]` and cap each user's daily contribution to a fraction of `dailyMintLimit`.
2. **Minimum deposit floor with queue**: Accept deposits up to the limit and queue the remainder, rather than reverting.
3. **Partial fill**: Allow a deposit to be partially filled up to the remaining daily capacity instead of reverting entirely when the limit would be exceeded.

---

### Proof of Concept

Assume `dailyMintLimit = 1000 ether` (in rsETH terms) and `feeBps = 50` (0.5%).

1. Attacker calls `deposit{value: X}("")` where `X` is chosen so that `viewSwapRsETHAmountAndFee(X).rsETHAmount == 1000 ether`.
2. Inside `limitDailyMint`: `dailyMintAmount (0) + 1000 ether <= 1000 ether` → passes. `dailyMintAmount` is set to `1000 ether`.
3. Attacker receives `1000 ether` of wrsETH. Cost: `~0.5%` of `X` in fees.
4. Any subsequent user calls `deposit{value: 1 wei}("")`. Inside `limitDailyMint`: `1000 ether + epsilon > 1000 ether` → `revert DailyMintLimitExceeded()`.
5. All deposits are blocked until `getCurrentDay()` increments (up to 24 hours).
6. At the start of the next day, attacker repeats step 1.

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
