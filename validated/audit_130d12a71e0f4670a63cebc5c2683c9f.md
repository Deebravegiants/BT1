### Title
`RSETH.setMaxMintAmountPerDay()` Accepts Zero Without Validation, Enabling Complete DoS on All Protocol Deposits — (File: `contracts/RSETH.sol`)

---

### Summary

`RSETH.setMaxMintAmountPerDay()` imposes no lower-bound check on its input. Setting it to `0` causes the `checkDailyMintLimit` modifier to revert on every non-zero mint call, permanently blocking all rsETH minting until corrected. Because every user deposit path through `LRTDepositPool` terminates in `RSETH.mint()`, this silently disables the protocol's core deposit functionality.

---

### Finding Description

`setMaxMintAmountPerDay()` is callable by the LRT Manager role and writes directly to `maxMintAmountPerDay` with no validation:

```solidity
// contracts/RSETH.sol L125-128
function setMaxMintAmountPerDay(uint256 _maxMintAmountPerDay) external onlyLRTManager {
    maxMintAmountPerDay = _maxMintAmountPerDay;
    emit MaxMintAmountPerDayUpdated(_maxMintAmountPerDay);
}
```

The `checkDailyMintLimit` modifier, applied to every `mint()` call, enforces:

```solidity
// contracts/RSETH.sol L50-52
if (currentPeriodMintedAmount + amount > maxMintAmountPerDay) {
    revert DailyMintLimitExceeded(currentPeriodMintedAmount + amount, maxMintAmountPerDay);
}
```

When `maxMintAmountPerDay == 0`, the condition reduces to `amount > 0`, which is true for every real deposit. The revert fires unconditionally.

The deposit entry points in `LRTDepositPool` both terminate in `_mintRsETH()` → `IRSETH.mint()`:

```solidity
// contracts/LRTDepositPool.sol L686-690
function _mintRsETH(uint256 rsethAmountToMint) private {
    address rsethToken = lrtConfig.rsETH();
    IRSETH(rsethToken).mint(msg.sender, rsethAmountToMint);
}
```

Because the deposit transaction reverts atomically, no ETH or LST is taken from the user, but the protocol is rendered unable to accept any new deposits for as long as the limit remains at zero.

---

### Impact Explanation

**Low — Contract fails to deliver promised returns, but doesn't lose value.**

All calls to `LRTDepositPool.depositETH()` and `LRTDepositPool.depositAsset()` revert. No user funds are lost (transactions revert), but the protocol's primary function — accepting deposits and issuing rsETH — is completely disabled. Existing rsETH holders and withdrawal flows are unaffected.

---

### Likelihood Explanation

**Low.** Triggering the condition requires the LRT Manager to call `setMaxMintAmountPerDay(0)`. This can occur through accidental misconfiguration (e.g., a scripting error passing `0` instead of a denominated token amount) or a UI/tooling bug. The absence of any on-chain guard makes such an error silently accepted with no revert or warning. The protocol also initialises `maxMintAmountPerDay` to `0` by default (not set in `initialize()`), meaning the window exists from deployment until the manager first configures a non-zero value.

---

### Recommendation

Add a non-zero guard in `setMaxMintAmountPerDay()`:

```solidity
function setMaxMintAmountPerDay(uint256 _maxMintAmountPerDay) external onlyLRTManager {
    if (_maxMintAmountPerDay == 0) revert InvalidMaxMintAmountPerDay();
    maxMintAmountPerDay = _maxMintAmountPerDay;
    emit MaxMintAmountPerDayUpdated(_maxMintAmountPerDay);
}
```

Apply the same pattern to `LRTOracle.setMaxFeeMintAmountPerDay()`, which has an identical structural issue: setting it to `0` causes `_checkAndUpdateDailyFeeMintLimit()` to revert whenever a non-zero protocol fee is due, blocking `updateRSETHPrice()` and staling the rsETH price feed.

---

### Proof of Concept

1. LRT Manager calls `RSETH.setMaxMintAmountPerDay(0)`.
2. Any user calls `LRTDepositPool.depositETH{value: 1 ether}(0, "")`.
3. Execution reaches `_mintRsETH(rsethAmountToMint)` → `IRSETH.mint(msg.sender, rsethAmountToMint)`.
4. `checkDailyMintLimit(rsethAmountToMint)` evaluates `0 + rsethAmountToMint > 0` → `true`.
5. Transaction reverts with `DailyMintLimitExceeded(rsethAmountToMint, 0)`.
6. All deposit paths are blocked until the manager resets the value. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

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

**File:** contracts/RSETH.sol (L125-128)
```text
    function setMaxMintAmountPerDay(uint256 _maxMintAmountPerDay) external onlyLRTManager {
        maxMintAmountPerDay = _maxMintAmountPerDay;
        emit MaxMintAmountPerDayUpdated(_maxMintAmountPerDay);
    }
```

**File:** contracts/LRTDepositPool.sol (L684-690)
```text
    /// @dev private function to mint rseth
    /// @param rsethAmountToMint Amount of rseth minted
    function _mintRsETH(uint256 rsethAmountToMint) private {
        address rsethToken = lrtConfig.rsETH();
        // mint rseth for user
        IRSETH(rsethToken).mint(msg.sender, rsethAmountToMint);
    }
```

**File:** contracts/LRTOracle.sol (L132-135)
```text
    function setMaxFeeMintAmountPerDay(uint256 _maxFeeMintAmountPerDay) external onlyLRTManager {
        maxFeeMintAmountPerDay = _maxFeeMintAmountPerDay;
        emit MaxFeeMintAmountPerDayUpdated(_maxFeeMintAmountPerDay);
    }
```

**File:** contracts/LRTOracle.sol (L204-207)
```text
        // Check if minting would exceed the daily limit
        if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
            revert DailyFeeMintLimitExceeded(currentPeriodMintedFeeAmount + feeAmount, maxFeeMintAmountPerDay);
        }
```
