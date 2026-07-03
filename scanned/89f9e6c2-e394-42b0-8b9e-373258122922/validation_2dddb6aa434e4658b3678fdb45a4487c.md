### Title
`LRTConfig::setProtocolFeeBps` update retrospectively applies new fee rate to all pending staking rewards not yet settled by the oracle - (File: contracts/LRTOracle.sol)

---

### Summary

`LRTConfig::setProtocolFeeBps` can update `protocolFeeInBPS` at any time while EigenLayer staking rewards are accumulating but not yet settled. When `LRTOracle::updateRSETHPrice()` is next called — by anyone, since it is a public function — the new (higher) fee rate is applied to the entire reward delta (`totalETHInProtocol − previousTVL`) that accrued since the last oracle update, including the portion that accrued under the previous lower fee regime. This is the direct structural analog of the Beefy `setBeefyFeeConfig` / `_harvest` race.

---

### Finding Description

**Root cause — two independent state mutations with no coupling:**

**Step 1 — fee update path (`LRTConfig.sol` L196–200):**

```solidity
function setProtocolFeeBps(uint256 _protocolFeeInBPS) external onlyRole(LRTConstants.MANAGER) {
    if (_protocolFeeInBPS > 1500) revert ProtocolFeeExceedsLimit();
    protocolFeeInBPS = _protocolFeeInBPS;          // ← immediate, no oracle flush
    emit UpdateFee(_protocolFeeInBPS);
}
```

`setProtocolFeeBps` writes the new rate directly to storage with no precondition that pending rewards be settled first.

**Step 2 — reward settlement path (`LRTOracle.sol` L244–246):**

```solidity
if (!protocolPaused && totalETHInProtocol > previousTVL) {
    uint256 rewardAmount = totalETHInProtocol - previousTVL;
    protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
}
```

`_updateRsETHPrice()` reads `lrtConfig.protocolFeeInBPS()` **at settlement time**, not at the time the rewards were earned. `rewardAmount` is the cumulative TVL growth since the last oracle call — it bundles together rewards that accrued across the entire inter-update window, regardless of what fee rate was in effect during that window.

**Step 3 — public trigger (`LRTOracle.sol` L87–89):**

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

`updateRSETHPrice()` carries no access control. Any address can call it.

**Combined exploit sequence:**

1. Protocol runs with `protocolFeeInBPS = 500` (5 %). Rewards accumulate in EigenLayer strategies over time; `rsETHPrice` is stale.
2. MANAGER calls `setProtocolFeeBps(1500)` (15 %, the maximum allowed).
3. Anyone (or the MANAGER itself) calls `updateRSETHPrice()`.
4. `rewardAmount` = entire TVL growth since the last oracle update (which may span days of 5 % accrual).
5. `protocolFeeInETH = rewardAmount × 1500 / 10 000` — 15 % is charged on rewards that users earned under the 5 % regime.
6. The excess fee (10 % of `rewardAmount`) is minted as rsETH to the protocol treasury, diluting all existing rsETH holders.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

The protocol treasury receives rsETH minted at the elevated fee rate on rewards that were generated while the lower fee was in effect. Every rsETH holder suffers dilution proportional to the fee increase applied to the unsettled reward window. The stolen amount scales with (a) the size of the accumulated reward delta and (b) the magnitude of the fee increase. At the maximum fee ceiling of 1500 BPS, the protocol can extract up to three times the legitimately owed fee on any unsettled reward window.

---

### Likelihood Explanation

The MANAGER role is a protocol-controlled key, not a timelock-gated multisig in the current deployment. `setProtocolFeeBps` requires only that role. `updateRSETHPrice()` is public and is expected to be called regularly (e.g., by keepers or any user). The oracle update interval is not enforced on-chain, so the reward window can be arbitrarily large. No additional preconditions, external dependencies, or user interaction are required beyond the MANAGER executing a single transaction.

---

### Recommendation

`LRTConfig::setProtocolFeeBps` should atomically flush the oracle before writing the new rate. Concretely:

1. `setProtocolFeeBps` should call `ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE)).updateRSETHPrice()` **before** updating `protocolFeeInBPS`, so that all rewards accrued under the old rate are settled at the old rate first.
2. Alternatively, `LRTOracle` can snapshot the fee rate at each update and apply it only to the reward delta earned since the previous update, rather than reading the live rate at settlement time.

This mirrors the Beefy mitigation: call `_claimEarnings` + `_chargeFees` before updating the fee config.

---

### Proof of Concept

```
State before exploit:
  protocolFeeInBPS  = 500   (5 %)
  rsETHPrice        = 1.05 ETH  (last settled 3 days ago)
  totalETHInProtocol (now) = 1_050_000 ETH
  previousTVL (rsethSupply × rsETHPrice) = 1_000_000 ETH
  rewardAmount (pending) = 50_000 ETH

Legitimate fee at 5 %:  50_000 × 500 / 10_000 = 2_500 ETH

Attack:
  Tx 1: MANAGER calls LRTConfig.setProtocolFeeBps(1500)
  Tx 2: anyone calls LRTOracle.updateRSETHPrice()

  rewardAmount      = 50_000 ETH
  protocolFeeInETH  = 50_000 × 1500 / 10_000 = 7_500 ETH

Excess fee extracted: 7_500 − 2_500 = 5_000 ETH worth of rsETH
minted to treasury at users' expense.
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/LRTConfig.sol (L196-200)
```text
    function setProtocolFeeBps(uint256 _protocolFeeInBPS) external onlyRole(LRTConstants.MANAGER) {
        if (_protocolFeeInBPS > 1500) revert ProtocolFeeExceedsLimit();
        protocolFeeInBPS = _protocolFeeInBPS;
        emit UpdateFee(_protocolFeeInBPS);
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L244-247)
```text
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }
```

**File:** contracts/LRTOracle.sol (L299-307)
```text
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
```
