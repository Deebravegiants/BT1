### Title
`rsETHPrice` Updated Unconditionally While Fee Calculation Is Skipped During Partial Pause — (`contracts/LRTOracle.sol`)

### Summary

`_updateRsETHPrice()` always writes the new price to `rsETHPrice` at line 313, even when the protocol-fee calculation was skipped because `protocolPaused == true`. This is the exact structural analog of the GMX M-8 bug: a state variable that serves as the fee-accounting baseline is advanced unconditionally, while the fee collection that should accompany that advance is conditionally omitted. Rewards that accrue while the deposit pool or withdrawal manager is paused permanently escape the protocol-fee mechanism.

### Finding Description

`LRTOracle._updateRsETHPrice()` computes `protocolPaused` as the logical OR of three independent pause flags:

```solidity
bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;
``` [1](#0-0) 

When `protocolPaused` is `true`, the fee calculation is skipped entirely:

```solidity
uint256 protocolFeeInETH = 0;
if (!protocolPaused && totalETHInProtocol > previousTVL) {
    uint256 rewardAmount = totalETHInProtocol - previousTVL;
    protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
}
``` [2](#0-1) 

However, `rsETHPrice` — the variable that encodes the fee-accounting baseline (`previousTVL = rsethSupply * rsETHPrice`) — is written unconditionally at the end of the same function:

```solidity
rsETHPrice = newRsETHPrice;
``` [3](#0-2) 

`updateRSETHPrice()` is a public function gated only by the oracle's own `whenNotPaused` modifier:

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [4](#0-3) 

The oracle's `paused` flag is independent of `lrtDepositPool.paused()` and `withdrawalManager.paused()`. Therefore, when either of the latter two is paused (a routine operational event — upgrades, security incidents, queue management) but the oracle itself is not, `updateRSETHPrice()` remains callable by anyone, `protocolPaused` evaluates to `true`, the fee is zeroed out, yet `rsETHPrice` is advanced to the full new TVL/supply ratio. On the next call after the pause is lifted, `previousTVL` is computed from the already-advanced `rsETHPrice`, so the rewards that accrued during the pause window are never subject to the fee.

### Impact Explanation

**High — Theft of unclaimed yield.**

The protocol treasury is the intended recipient of `protocolFeeInBPS` of all staking rewards. Every time `updateRSETHPrice()` is called while the deposit pool or withdrawal manager is paused, the entire reward delta for that period is permanently excluded from fee collection. The treasury receives zero fee on those rewards; rsETH holders receive the full price appreciation instead. The loss scales with the size of the reward delta and the fee rate, and is irreversible once `rsETHPrice` has been advanced.

### Likelihood Explanation

**Medium.**

The deposit pool and withdrawal manager are paused regularly for operational reasons (upgrades, EigenLayer queue management, security incidents). The oracle is not co-paused in these scenarios — the downside-protection auto-pause only fires when the oracle itself detects an out-of-limit price drop and explicitly calls `_pause()`. During any ordinary operational pause of the deposit pool or withdrawal manager, `updateRSETHPrice()` remains open to the public. Any rsETH holder is economically incentivized to call it: doing so advances the price baseline without the fee dilution that would otherwise reduce their per-share value.

### Recommendation

Mirror the GMX recommendation exactly: do not advance `rsETHPrice` when the fee calculation was skipped. Either:

1. **Guard the price write** — only commit `rsETHPrice = newRsETHPrice` when `protocolFeeInETH` was actually computed (i.e., when `!protocolPaused`), or
2. **Defer the baseline** — when `protocolPaused`, compute and store `newRsETHPrice` for display purposes but do not update the stored `rsETHPrice` that feeds `previousTVL` on the next call.

Option 2 is safer because it also prevents the `highestRsethPrice` ratchet from advancing during a pause, which has its own implications for the downside-protection threshold.

### Proof of Concept

1. Protocol is live; `rsETHPrice = 1.05 ETH`, `rsethSupply = 1 000 000`, `protocolFeeInBPS = 1000` (10 %).
2. Admin pauses `LRTDepositPool` for an upgrade. Oracle is **not** paused.
3. EigenLayer staking rewards accrue; `totalETHInProtocol` grows by `1 000 ETH` (i.e., `previousTVL + 1 000 ETH`).
4. An rsETH holder calls `updateRSETHPrice()`.
   - `protocolPaused = true` (deposit pool is paused).
   - `protocolFeeInETH = 0` (fee skipped).
   - `newRsETHPrice = (1 050 000 + 1 000) / 1 000 000 = 1.051 ETH`.
   - `rsETHPrice = 1.051 ETH` ← baseline advanced.
5. Admin unpauses `LRTDepositPool`.
6. Next `updateRSETHPrice()` call: `previousTVL = 1 000 000 * 1.051 = 1 051 000 ETH`. The 1 000 ETH reward from step 3 is already baked in; no fee is ever collected on it.
7. Treasury loses `1 000 * 10% = 100 ETH` worth of fee. rsETH holders retain it. [5](#0-4) [3](#0-2)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L234-250)
```text
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
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```
