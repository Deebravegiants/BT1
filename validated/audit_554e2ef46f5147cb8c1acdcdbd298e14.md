### Title
Shared `dailyMintLimit` Can Be Exhausted by Any Depositor, Temporarily Freezing All Subsequent Deposits - (File: contracts/pools/RSETHPoolV3.sol)

---

### Summary

The `limitDailyMint` modifier in `RSETHPoolV3` (and its variants) maintains a single shared `dailyMintAmount` counter that accumulates across all user deposits within a UTC-day window. Any depositor — including a malicious one — can fill this counter to `dailyMintLimit` in a single transaction, causing every subsequent deposit call in that day to revert with `DailyMintLimitExceeded`. Because the attacker receives `wrsETH` in exchange for their deposit, the net cost of the attack is only gas.

---

### Finding Description

The `limitDailyMint` modifier is applied to both `deposit(string)` (ETH) and `deposit(address,uint256,string)` (ERC-20) in `RSETHPoolV3`:

```solidity
// contracts/pools/RSETHPoolV3.sol  lines 96-125
modifier limitDailyMint(uint256 amount, address token) {
    ...
    uint256 currentDay = getCurrentDay();
    if (currentDay > lastMintDay) {
        lastMintDay = currentDay;
        dailyMintAmount = 0;          // reset once per day
    }
    if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
        revert DailyMintLimitExceeded();   // shared limit
    }
    dailyMintAmount += rsETHAmount;        // accumulates for ALL users
    _;
}
```

`dailyMintAmount` is a single storage slot shared by every caller. There is no per-user sub-limit and no mechanism to reserve capacity for pending transactions. An attacker who deposits enough ETH (or a supported LST) to push `dailyMintAmount` to `dailyMintLimit` atomically blocks every other depositor for the remainder of the 24-hour window.

The identical pattern exists in:
- `RSETHPoolV3ExternalBridge.sol` (lines 130-159)
- `RSETHPoolV3WithNativeChainBridge.sol` (lines 121-137)
- `RSETHPoolV2ExternalBridge.sol` (lines 104-126)
- `RSETH.sol` — `checkDailyMintLimit` modifier (lines 42-56), which gates the L1 `mint()` call made by `LRTDepositPool`

---

### Impact Explanation

Every user who calls `deposit` after the limit is exhausted receives a revert. Their ETH/LST is returned, but they are locked out of the protocol for up to 24 hours. Because the L2 pools are the primary on-ramp for rsETH on each chain, exhausting the limit effectively freezes all new deposits on that chain for the remainder of the day. This maps to **Medium — Temporary freezing of funds**.

---

### Likelihood Explanation

The attack is cheap. The attacker deposits ETH and receives `wrsETH` — a liquid, yield-bearing token — in return. The net out-of-pocket cost is only the gas for one transaction. The attacker suffers no economic loss; they simply hold `wrsETH` (or sell it on a secondary market). Because the attack is profitable-neutral and requires no special role, any externally-owned account can execute it at any time during the day. Likelihood is **High**.

---

### Recommendation

1. **Do not revert on limit exhaustion for individual users.** Instead, cap the minted amount to the remaining daily quota and refund the excess ETH/tokens, or queue the remainder.
2. **Alternatively**, track the limit at the protocol level only (not per-transaction) and allow partial fills so that a single large deposit cannot block all subsequent ones.
3. **Add a per-address sub-limit** so that no single depositor can consume the entire daily quota.
4. **Emit an event** when the daily limit is near exhaustion so off-chain monitoring can alert operators before the limit is fully consumed.

---

### Proof of Concept

**Setup:** `dailyMintLimit = 1000 wrsETH`. Current `dailyMintAmount = 0`.

**Step 1 — Attacker deposits:**
```
attacker calls deposit{value: X ETH}("") 
  → limitDailyMint computes rsETHAmount ≈ 1000 wrsETH
  → dailyMintAmount becomes 1000 (== dailyMintLimit)
  → attacker receives 1000 wrsETH
```

**Step 2 — Victim deposits (same day, any block):**
```
victim calls deposit{value: 0.01 ETH}("")
  → limitDailyMint: dailyMintAmount(1000) + rsETHAmount(~0.01) > dailyMintLimit(1000)
  → revert DailyMintLimitExceeded()
```

**Step 3 — Victim is locked out** for up to 24 hours. The attacker holds `wrsETH` worth approximately the ETH they deposited — no net loss.

The same sequence applies on L1 via `LRTDepositPool.depositETH` → `RSETH.mint` → `checkDailyMintLimit`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

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

**File:** contracts/RSETH.sol (L42-56)
```text
    modifier checkDailyMintLimit(uint256 amount) {
        // Check if we need to reset the period if it has been more than 24 hours
        if (block.timestamp >= periodStartTime + 1 days) {
            currentPeriodMintedAmount = 0;
            periodStartTime = getCurrentPeriodStartTime();
        }

        // Check if minting would exceed the daily limit
        if (currentPeriodMintedAmount + amount > maxMintAmountPerDay) {
            revert DailyMintLimitExceeded(currentPeriodMintedAmount + amount, maxMintAmountPerDay);
        }

        currentPeriodMintedAmount += amount;
        _;
    }
```

**File:** contracts/RSETH.sol (L229-240)
```text
    function mint(
        address to,
        uint256 amount
    )
        external
        onlyRole(LRTConstants.MINTER_ROLE)
        whenNotPaused
        checkDailyMintLimit(amount)
    {
        _enforceNotBlocked(to);
        _mint(to, amount);
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

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L104-126)
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
