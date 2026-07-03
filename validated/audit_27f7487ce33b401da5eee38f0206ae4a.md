### Title
Protocol Fee Rate Change Applied Retroactively to Accumulated Rewards Without Prior Price Settlement - (File: `contracts/LRTConfig.sol`)

---

### Summary

`setProtocolFeeBps` in `LRTConfig` updates `protocolFeeInBPS` without first triggering `updateRSETHPrice()` in `LRTOracle`. Because `_updateRsETHPrice` computes the protocol fee against **all rewards accumulated since the last price update**, a fee rate increase retroactively taxes rewards that accrued under the old, lower rate — stealing yield from rsETH holders.

---

### Finding Description

`LRTConfig.setProtocolFeeBps` is the direct analog to Ion Protocol's `updateInterestRateModule`. It changes the fee rate parameter that governs how much of the protocol's yield is extracted as a fee, but it does not first settle the current reward period:

```solidity
// contracts/LRTConfig.sol
function setProtocolFeeBps(uint256 _protocolFeeInBPS) external onlyRole(LRTConstants.MANAGER) {
    if (_protocolFeeInBPS > 1500) revert ProtocolFeeExceedsLimit();
    protocolFeeInBPS = _protocolFeeInBPS;   // ← no updateRSETHPrice() call before this
    emit UpdateFee(_protocolFeeInBPS);
}
```

When `updateRSETHPrice()` is next called (by anyone — it is `public`), `_updateRsETHPrice` computes the reward amount as the **entire TVL growth since the last price snapshot**:

```solidity
// contracts/LRTOracle.sol
uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);          // price from last update
// ...
uint256 rewardAmount = totalETHInProtocol - previousTVL;       // all accumulated rewards
protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;  // new rate applied to old rewards
```

`rsETHPrice` is only updated at the end of `_updateRsETHPrice`. Between two consecutive calls, `previousTVL` is anchored to the old price. Any rewards that accrued during the interval — regardless of what fee rate was in effect at the time — are taxed at whatever `protocolFeeInBPS` is at the moment of the next call.

If the MANAGER raises the fee (e.g., from 5 % to 15 %) without first calling `updateRSETHPrice()`, the next invocation of `updateRSETHPrice()` applies 15 % to the entire accumulated reward, including the portion that accrued while the rate was 5 %. The excess fee is minted as rsETH to the treasury, diluting all existing rsETH holders.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

rsETH holders earn yield through appreciation of the rsETH/ETH exchange rate. When the fee is retroactively applied at a higher rate, the treasury is minted more rsETH than it is entitled to, and the new rsETH price is set lower than it should be. Every rsETH holder suffers a proportional loss of accrued-but-unsettled yield. The magnitude scales with (a) the size of the accumulated reward and (b) the fee rate delta. With a maximum fee of 1500 bps (15 %) and a prior rate of 0 %, the entire accumulated reward period could be taxed at 15 % instead of 0 %.

---

### Likelihood Explanation

**Low.**

Requires the MANAGER role to call `setProtocolFeeBps` without first calling `updateRSETHPrice()`. This is a plausible operational mistake (e.g., during a fee adjustment governance action that does not include a price-settlement step), not a deliberate attack. The Ion Protocol team acknowledged the exact same pattern as a known design trade-off. The likelihood is low but non-zero in normal protocol operations.

---

### Recommendation

Call `updateRSETHPrice()` (or the internal `_updateRsETHPrice()`) inside `setProtocolFeeBps` before updating `protocolFeeInBPS`, so that all rewards accumulated under the old rate are settled first and the new rate only applies to future rewards:

```solidity
function setProtocolFeeBps(uint256 _protocolFeeInBPS) external onlyRole(LRTConstants.MANAGER) {
    if (_protocolFeeInBPS > 1500) revert ProtocolFeeExceedsLimit();
    // Settle current rewards at the old rate before changing the fee
    ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE)).updateRSETHPrice();
    protocolFeeInBPS = _protocolFeeInBPS;
    emit UpdateFee(_protocolFeeInBPS);
}
```

If the oracle is paused and `updateRSETHPrice()` would revert, the function should at minimum document that the caller must manually settle before changing the fee.

---

### Proof of Concept

1. Protocol runs for 7 days with `protocolFeeInBPS = 500` (5 %). `updateRSETHPrice()` was last called 7 days ago, setting `rsETHPrice = P0`.
2. During those 7 days, staking rewards cause `totalETHInProtocol` to grow by `R` ETH above `previousTVL = rsethSupply × P0`.
3. MANAGER calls `setProtocolFeeBps(1500)` (15 %) without first calling `updateRSETHPrice()`.
4. Any caller (unprivileged) calls `updateRSETHPrice()`.
5. Inside `_updateRsETHPrice`:
   - `rewardAmount = totalETHInProtocol − previousTVL = R`
   - `protocolFeeInETH = R × 1500 / 10_000 = 0.15R` ← should be `0.05R`
   - Treasury is minted rsETH worth `0.10R` ETH more than it deserves.
   - `newRsETHPrice` is depressed by the excess fee, permanently reducing the value of every rsETH holder's position.

The excess `0.10R` ETH worth of rsETH is irreversibly minted to the treasury at the expense of all rsETH holders.

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/LRTConfig.sol (L196-199)
```text
    function setProtocolFeeBps(uint256 _protocolFeeInBPS) external onlyRole(LRTConstants.MANAGER) {
        if (_protocolFeeInBPS > 1500) revert ProtocolFeeExceedsLimit();
        protocolFeeInBPS = _protocolFeeInBPS;
        emit UpdateFee(_protocolFeeInBPS);
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L233-246)
```text
        // calculate previousTVL using rsethSupply multiplied by rsETHPrice
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);

        IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

        // determine if the protocol is active (not paused)
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;

        // only take fee if TVL increased and protocol is not paused
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
```
