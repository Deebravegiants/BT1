### Title
Attacker Can Permanently Exhaust the Daily Mint Limit to DoS All Deposits — (`contracts/pools/RSETHPoolV3.sol`, `contracts/pools/RSETHPoolV3ExternalBridge.sol`, `contracts/pools/RSETHPoolV3WithNativeChainBridge.sol`)

---

### Summary

The `limitDailyMint` modifier in all three L2 pool variants tracks cumulative minted rsETH in `dailyMintAmount`, which is only ever incremented on deposit and reset once per calendar day. There is no public path to decrement it. An unprivileged depositor can consume the entire daily limit in a single transaction, causing every subsequent deposit within that 24-hour window to revert with `DailyMintLimitExceeded`. The attacker retains the wrsETH they received (a yield-bearing asset), so the attack carries no net financial cost.

---

### Finding Description

The `limitDailyMint` modifier is applied to every public `deposit` entry point across `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, and `RSETHPoolV3WithNativeChainBridge`:

```solidity
modifier limitDailyMint(uint256 amount, address token) {
    ...
    if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
        revert DailyMintLimitExceeded();
    }
    dailyMintAmount += rsETHAmount;   // ← only ever increases
    _;
}
```

`dailyMintAmount` is incremented on every successful deposit and is only reset to zero when `getCurrentDay() > lastMintDay` — i.e., once per 24-hour period. There is no mechanism that decrements it. The only function that could conceptually reverse a deposit (`swapAssetToPremintedRsETH`) is gated behind `OPERATOR_ROLE` and does not touch `dailyMintAmount` at all.

An attacker who deposits an amount large enough to push `dailyMintAmount` to `dailyMintLimit` leaves the modifier in a permanently-blocking state for the rest of the day. All subsequent callers — regardless of deposit size — will revert. The attacker receives wrsETH in exchange, which is a yield-bearing L2 wrapper for rsETH and can be held, bridged, or sold on secondary markets. The attacker suffers no economic loss.

---

### Impact Explanation

**Impact: Medium — Temporary freezing of funds.**

All deposit paths (`deposit(string)` for ETH and `deposit(address,uint256,string)` for tokens) are blocked for up to 24 hours across every affected L2 pool. Users who need to enter the protocol during that window are completely denied service. The freeze is self-resolving at the next day boundary, but can be repeated every day at zero cost to the attacker.

---

### Likelihood Explanation

**Likelihood: Medium.**

Any address with sufficient capital to reach `dailyMintLimit` can execute this attack. The attacker retains full economic value (wrsETH ≈ ETH in value), so the only barrier is capital availability, not willingness to lose funds. On chains where the daily limit is set conservatively (e.g., to limit bridge risk), the capital requirement may be modest. The attack can be repeated every 24 hours indefinitely.

---

### Recommendation

1. **Decrement `dailyMintAmount` on reverse swaps.** If `swapAssetToPremintedRsETH` is ever made accessible to users, it should reduce `dailyMintAmount` by the corresponding rsETH amount.
2. **Rate-limit per depositor** rather than (or in addition to) globally, so a single actor cannot exhaust the shared limit.
3. **Allow the admin to reset `dailyMintAmount`** in an emergency without waiting for the next calendar day.
4. **Consider a per-transaction cap** (maximum single deposit size) to raise the cost of limit exhaustion without removing the global safety rail.

---

### Proof of Concept

```
// Affected: RSETHPoolV3.sol (same pattern in ExternalBridge and NativeChainBridge variants)

// 1. Attacker observes dailyMintLimit = L (e.g. 100 ETH worth of rsETH)
// 2. Attacker calls:
pool.deposit{value: L_in_ETH}("ref");
//    → limitDailyMint runs: dailyMintAmount += L  (now == dailyMintLimit)
//    → attacker receives wrsETH worth ~L ETH

// 3. Any subsequent user deposit in the same day:
pool.deposit{value: 1 ether}("ref");
//    → limitDailyMint: dailyMintAmount + rsETHAmount > dailyMintLimit
//    → revert DailyMintLimitExceeded()   ← DoS

// 4. Attacker holds wrsETH (no loss). Repeats next day.
// dailyMintAmount is never decremented; no public path exists to reduce it.
```

The root cause lines are: [1](#0-0) [2](#0-1) [3](#0-2) 

The operator-only reverse-swap that does **not** decrement `dailyMintAmount`: [4](#0-3)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L119-123)
```text
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
```

**File:** contracts/pools/RSETHPoolV3.sol (L414-450)
```text
    function swapAssetToPremintedRsETH(
        address rsETH,
        address token,
        uint256 rsETHAmount
    )
        external
        nonReentrant
        onlySupportedTokenOrEth(token)
        onlyRole(OPERATOR_ROLE)
    {
        UtilLib.checkNonZeroAddress(rsETH);

        IRsETHTokenWrapper wrapper = IRsETHTokenWrapper(address(wrsETH));
        IERC20 tokenContract = IERC20(token);

        if (!wrapper.allowedTokens(rsETH)) revert TokenNotAllowedInWrapper();
        if (rsETHAmount == 0) revert InvalidAmount();
        if (rsETHAmount > wrapper.maxAmountToDepositBridgerAsset(rsETH)) revert ExceedsMaxAmountToDepositInWrapper();

        // Get the amount of token to transfer to the user for the given amount of rsETH provided
        uint256 tokenAmount = viewSwapAssetToPremintedRsETH(token, rsETHAmount);

        // Transfer rsETH from sender to the wrapper
        IERC20(rsETH).safeTransferFrom(msg.sender, address(wrapper), rsETHAmount);

        // Transfer the token from the pool to the sender
        if (token == ETH_IDENTIFIER) {
            if (getETHBalanceMinusFees() < tokenAmount) revert InsufficientETHBalanceForReverseSwap();
            (bool success,) = payable(msg.sender).call{ value: tokenAmount }("");
            if (!success) revert TransferFailed();
        } else {
            if (getTokenBalanceMinusFees(token) < tokenAmount) revert InsufficientAssetBalanceForReverseSwap();
            tokenContract.safeTransfer(msg.sender, tokenAmount);
        }

        emit ReverseSwapOccurred(msg.sender, rsETH, token, rsETHAmount, tokenAmount);
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L153-157)
```text
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L131-135)
```text
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
```
