### Title
`setProtocolFeeBps()` Changes Fee Rate Without Prior Reward Accrual, Retroactively Distorting Yield Distribution - (File: contracts/LRTConfig.sol)

---

### Summary

`LRTConfig.setProtocolFeeBps()` updates `protocolFeeInBPS` immediately without first calling `LRTOracle.updateRSETHPrice()` to settle pending rewards at the old rate. Because `_updateRsETHPrice()` reads `protocolFeeInBPS` at call time and applies it to **all rewards accumulated since the last price update**, a fee rate increase retroactively taxes rewards that accrued under the previous (lower) rate, transferring yield from rsETH holders to the protocol treasury.

---

### Finding Description

`LRTOracle._updateRsETHPrice()` computes the protocol fee on the entire reward delta since the last stored price:

```
rewardAmount    = totalETHInProtocol - (rsethSupply * rsETHPrice)   // all pending rewards
protocolFeeInETH = rewardAmount * lrtConfig.protocolFeeInBPS() / 10_000
```

`rsETHPrice` is only updated when `updateRSETHPrice()` is called. Between two consecutive calls, rewards accumulate. The fee applied to those rewards is whatever `protocolFeeInBPS` is **at the moment of the next call**, not the rate in effect when the rewards were earned.

`LRTConfig.setProtocolFeeBps()` performs a bare storage write with no prior accrual:

```solidity
function setProtocolFeeBps(uint256 _protocolFeeInBPS) external onlyRole(LRTConstants.MANAGER) {
    if (_protocolFeeInBPS > 1500) revert ProtocolFeeExceedsLimit();
    protocolFeeInBPS = _protocolFeeInBPS;   // ← no updateRSETHPrice() call first
    emit UpdateFee(_protocolFeeInBPS);
}
```

The correct pattern (as recommended in the reference report) is to call the accrual function **before** changing the parameter, so that all rewards earned under the old rate are settled at that rate before the new rate takes effect.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

When the MANAGER raises `protocolFeeInBPS` (e.g., from 500 bps to 1500 bps) without first calling `updateRSETHPrice()`, the next price update applies the new 15% fee to rewards that accrued entirely under the old 5% rate. The excess 10% of those rewards is minted as rsETH to the protocol treasury instead of remaining in the rsETH price, permanently reducing the value of every rsETH holder's position for that accrual window. The magnitude scales with the size of the pending reward delta and the fee increase.

---

### Likelihood Explanation

**Low.** The MANAGER role is a privileged, trusted role. However, the protocol provides no enforcement mechanism (no modifier, no internal call) that forces `updateRSETHPrice()` to be called before `setProtocolFeeBps()`. A well-intentioned MANAGER performing a routine fee adjustment can inadvertently trigger this distortion without any awareness of the ordering requirement. The risk is elevated because `updateRSETHPrice()` is a separate, unrelated-looking public function in a different contract (`LRTOracle`), making the dependency non-obvious.

---

### Recommendation

Call `updateRSETHPrice()` (or its internal equivalent) inside `setProtocolFeeBps()` before updating the fee, so all rewards accumulated under the old rate are settled first:

```solidity
function setProtocolFeeBps(uint256 _protocolFeeInBPS) external onlyRole(LRTConstants.MANAGER) {
    if (_protocolFeeInBPS > 1500) revert ProtocolFeeExceedsLimit();
    // Settle pending rewards at the current fee rate before changing it
    ILRTOracle(contractMap[LRTConstants.LRT_ORACLE]).updateRSETHPrice();
    protocolFeeInBPS = _protocolFeeInBPS;
    emit UpdateFee(_protocolFeeInBPS);
}
```

---

### Proof of Concept

**Setup:**
- `protocolFeeInBPS = 500` (5%)
- `rsETHPrice = 1.0 ETH` (last stored)
- `rsethSupply = 1000 rsETH`
- `totalETHInProtocol = 1100 ETH` (100 ETH of rewards have accrued since last update)

**Step 1:** MANAGER calls `LRTConfig.setProtocolFeeBps(1500)` (raise fee to 15%).
- `protocolFeeInBPS` is now 1500. No price update occurs.

**Step 2:** Anyone calls `LRTOracle.updateRSETHPrice()`.
- `previousTVL = 1000 * 1.0 = 1000 ETH`
- `rewardAmount = 1100 - 1000 = 100 ETH`
- `protocolFeeInETH = 100 * 1500 / 10_000 = 15 ETH` ← taxed at new 15% rate
- `newRsETHPrice = (1100 - 15) / 1000 = 1.085 ETH`

**Expected (correct) behavior** — if `updateRSETHPrice()` had been called before the fee change:
- `protocolFeeInETH = 100 * 500 / 10_000 = 5 ETH` ← taxed at old 5% rate
- `newRsETHPrice = (1100 - 5) / 1000 = 1.095 ETH`

**Difference:** rsETH holders receive a price of 1.085 instead of 1.095 — a loss of 0.01 ETH per rsETH (10 ETH total across 1000 rsETH), transferred to the treasury as excess fee mint. This is a direct, permanent reduction in rsETH holder yield for that accrual window. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/LRTConfig.sol (L194-200)
```text
    /// @dev Set the protocol fee bps
    /// @param _protocolFeeInBPS protocol fee bps
    function setProtocolFeeBps(uint256 _protocolFeeInBPS) external onlyRole(LRTConstants.MANAGER) {
        if (_protocolFeeInBPS > 1500) revert ProtocolFeeExceedsLimit();
        protocolFeeInBPS = _protocolFeeInBPS;
        emit UpdateFee(_protocolFeeInBPS);
    }
```

**File:** contracts/LRTOracle.sol (L228-234)
```text
        uint256 previousPrice = rsETHPrice;

        // get total ETH in the protocol (normalized to 1e18)
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

        // calculate previousTVL using rsethSupply multiplied by rsETHPrice
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);
```

**File:** contracts/LRTOracle.sol (L243-247)
```text
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }
```

**File:** contracts/LRTOracle.sol (L298-308)
```text
        // mint protocol fee as rsETH if there's a fee to take
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
