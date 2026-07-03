### Title
MANAGER Can Immediately Raise Protocol Fee and Remove Daily Fee Minting Cap Without Time Delay, Diluting rsETH Holders - (File: contracts/LRTOracle.sol)

### Summary
The `MANAGER` role can atomically raise `protocolFeeInBPS` to its maximum (1500 BPS) via `LRTConfig.setProtocolFeeBps` and set `maxFeeMintAmountPerDay` to an unbounded value via `LRTOracle.setMaxFeeMintAmountPerDay`, then immediately trigger `updateRSETHPrice()`. Because neither setter enforces a time delay, rsETH holders have no opportunity to exit before the fee extraction takes effect, directly diluting their yield.

### Finding Description
`LRTOracle._updateRsETHPrice()` mints rsETH to the treasury as a protocol fee on every price update:

```
protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
...
rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);
_checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
```

Two MANAGER-controlled parameters govern how much is extracted:

**Parameter 1 — `protocolFeeInBPS`** (`LRTConfig.sol` line 196–199):
```solidity
function setProtocolFeeBps(uint256 _protocolFeeInBPS) external onlyRole(LRTConstants.MANAGER) {
    if (_protocolFeeInBPS > 1500) revert ProtocolFeeExceedsLimit();
    protocolFeeInBPS = _protocolFeeInBPS;
    emit UpdateFee(_protocolFeeInBPS);
}
```
The MANAGER can raise the fee rate from 0 to 1500 BPS (15%) in a single transaction with no time delay.

**Parameter 2 — `maxFeeMintAmountPerDay`** (`LRTOracle.sol` line 132–135):
```solidity
function setMaxFeeMintAmountPerDay(uint256 _maxFeeMintAmountPerDay) external onlyLRTManager {
    maxFeeMintAmountPerDay = _maxFeeMintAmountPerDay;
    emit MaxFeeMintAmountPerDayUpdated(_maxFeeMintAmountPerDay);
}
```
There is **no upper bound check** and **no time delay**. Setting this to `type(uint256).max` makes `_checkAndUpdateDailyFeeMintLimit` a no-op, removing the only remaining safety cap on fee minting.

The daily cap check (`LRTOracle.sol` line 205):
```solidity
if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
    revert DailyFeeMintLimitExceeded(...);
}
```
…never triggers when `maxFeeMintAmountPerDay == type(uint256).max`.

This is a direct analog to the SetToken finding: just as the SetToken manager could remove and re-add the `StreamingFeeModule` to bypass the agreed fee cap, the LRT-rsETH MANAGER can atomically raise the fee rate to its maximum and nullify the daily minting cap — all without any time delay that would allow users to exit.

### Impact Explanation
Every rsETH holder is diluted. When `protocolFeeInETH > 0`, the new rsETH price is computed as:
```
newRsETHPrice = (totalETHInProtocol - protocolFeeInETH) / rsethSupply
```
and additional rsETH is minted to the treasury. With `protocolFeeInBPS = 1500` and `maxFeeMintAmountPerDay = type(uint256).max`, the MANAGER can extract up to 15% of all accrued rewards in a single `updateRSETHPrice()` call, with no daily ceiling. This constitutes **theft of unclaimed yield** from all rsETH holders — their rsETH is worth less ETH than it was before the fee extraction.

**Impact: High — Theft of unclaimed yield.**

### Likelihood Explanation
The MANAGER role (`keccak256("MANAGER")`) is a distinct role from `DEFAULT_ADMIN_ROLE` and `OPERATOR_ROLE`. A single MANAGER key-holder acting alone can execute the full attack sequence in two transactions (one to set parameters, one to trigger `updateRSETHPrice()`). No collusion with other roles is required. The attack is silent — only an `UpdateFee` event and a `MaxFeeMintAmountPerDayUpdated` event are emitted before the price update, giving holders no practical window to react on-chain.

**Likelihood: Medium** — requires a malicious or compromised MANAGER, but no other party's cooperation.

### Recommendation
1. Gate both `setProtocolFeeBps` and `setMaxFeeMintAmountPerDay` behind `TIME_LOCK_ROLE` (already defined in `LRTConstants`) so that a timelock contract enforces a mandatory delay before changes take effect.
2. Add an explicit upper bound to `setMaxFeeMintAmountPerDay` (e.g., a protocol-defined constant) so the daily cap cannot be set to an arbitrarily large value even by the timelock.
3. Emit a pending-change event at proposal time and a separate execution event after the delay, giving rsETH holders an observable window to exit.

### Proof of Concept
```
// Step 1 — MANAGER atomically maximises fee extraction
LRTConfig.setProtocolFeeBps(1500);                          // 15% fee, no delay
LRTOracle.setMaxFeeMintAmountPerDay(type(uint256).max);     // remove daily cap, no delay

// Step 2 — anyone (or the MANAGER) triggers the price update
LRTOracle.updateRSETHPrice();
// _updateRsETHPrice() computes:
//   rewardAmount = totalETHInProtocol - previousTVL
//   protocolFeeInETH = rewardAmount * 1500 / 10_000   (15%)
//   rsethAmountToMintAsProtocolFee = protocolFeeInETH / newRsETHPrice
//   _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee)
//     → 0 + rsethAmountToMintAsProtocolFee > type(uint256).max  → FALSE → no revert
//   IRSETH.mint(treasury, rsethAmountToMintAsProtocolFee)   ← yield stolen from holders
```

All rsETH holders receive a lower ETH redemption value immediately after Step 2, with no time delay between the MANAGER's parameter changes and the fee extraction. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTConfig.sol (L196-199)
```text
    function setProtocolFeeBps(uint256 _protocolFeeInBPS) external onlyRole(LRTConstants.MANAGER) {
        if (_protocolFeeInBPS > 1500) revert ProtocolFeeExceedsLimit();
        protocolFeeInBPS = _protocolFeeInBPS;
        emit UpdateFee(_protocolFeeInBPS);
```

**File:** contracts/LRTOracle.sol (L132-135)
```text
    function setMaxFeeMintAmountPerDay(uint256 _maxFeeMintAmountPerDay) external onlyLRTManager {
        maxFeeMintAmountPerDay = _maxFeeMintAmountPerDay;
        emit MaxFeeMintAmountPerDayUpdated(_maxFeeMintAmountPerDay);
    }
```

**File:** contracts/LRTOracle.sol (L197-210)
```text
    function _checkAndUpdateDailyFeeMintLimit(uint256 feeAmount) internal {
        // Reset the period if it's unset or a day has passed
        if (block.timestamp >= feePeriodStartTime + 1 days) {
            currentPeriodMintedFeeAmount = 0;
            feePeriodStartTime = getCurrentPeriodStartTime();
        }

        // Check if minting would exceed the daily limit
        if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
            revert DailyFeeMintLimitExceeded(currentPeriodMintedFeeAmount + feeAmount, maxFeeMintAmountPerDay);
        }

        currentPeriodMintedFeeAmount += feeAmount;
    }
```

**File:** contracts/LRTOracle.sol (L243-250)
```text
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L299-308)
```text
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
            }
```
