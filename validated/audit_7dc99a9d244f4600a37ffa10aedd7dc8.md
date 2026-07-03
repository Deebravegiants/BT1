### Title
Stale `rsETHPrice` Causes Retroactive Fee Application When `protocolFeeInBPS` Is Changed Without Triggering `updateRSETHPrice()` - (File: contracts/LRTConfig.sol, contracts/LRTOracle.sol)

### Summary
`LRTConfig.setProtocolFeeBps()` updates `protocolFeeInBPS` without first snapshotting the current `rsETHPrice` via `LRTOracle.updateRSETHPrice()`. The next call to `updateRSETHPrice()` — which is public and callable by anyone — retroactively applies the new fee rate to all rewards that accrued since the last price update, including rewards that accrued under the old fee rate.

### Finding Description
`LRTOracle._updateRsETHPrice()` computes the protocol fee as:

```
rewardAmount = totalETHInProtocol - (rsethSupply * rsETHPrice)   // rsETHPrice is stale
protocolFeeInETH = rewardAmount * lrtConfig.protocolFeeInBPS() / 10_000
``` [1](#0-0) 

`rsETHPrice` is a stored state variable that is only updated when `_updateRsETHPrice()` runs. `rewardAmount` therefore represents all ETH gains since the **last price update**, not since the fee change. When `setProtocolFeeBps()` raises the fee, the new rate is applied to the entire accumulated `rewardAmount`, including the portion that accrued while the old (lower) fee was in effect. [2](#0-1) 

`setProtocolFeeBps()` makes no call to `LRTOracle.updateRSETHPrice()` before writing the new fee. [3](#0-2) 

`updateRSETHPrice()` is public and permissionless, so any external caller can trigger the retroactive fee application immediately after the fee change.

### Impact Explanation
**High — Theft of unclaimed yield.**

When `protocolFeeInBPS` is raised (e.g., from 500 to 1500 BPS), the next `updateRSETHPrice()` call applies the new 15% rate to all rewards accumulated since the last price update — including rewards that accrued when the fee was only 5%. The excess fee is minted as rsETH to the treasury, permanently diluting existing rsETH holders' share of the TVL. The yield that belonged to rsETH holders is transferred to the protocol treasury without their consent and without any on-chain mechanism to recover it.

Conversely, a fee decrease causes the protocol to under-collect fees, but that scenario harms the protocol rather than users.

### Likelihood Explanation
The manager role is a privileged but non-admin role that is expected to adjust protocol parameters in normal operation. Fee adjustments are routine governance actions. The `updateRSETHPrice()` function is public and is called regularly (by bots, keepers, or any user). The window between a fee increase and the next price update is the attack surface — no special attacker action is needed beyond the fee change itself.

### Recommendation
Call `LRTOracle(_lrtOracle).updateRSETHPrice()` inside `setProtocolFeeBps()` before writing the new fee value, so that all rewards accrued under the old rate are settled at the old rate first:

```solidity
function setProtocolFeeBps(uint256 _protocolFeeInBPS) external onlyRole(LRTConstants.MANAGER) {
    if (_protocolFeeInBPS > 1500) revert ProtocolFeeExceedsLimit();
    // Settle accrued rewards at the current fee rate before changing it
    ILRTOracle(contractMap[LRTConstants.LRT_ORACLE]).updateRSETHPrice();
    protocolFeeInBPS = _protocolFeeInBPS;
    emit UpdateFee(_protocolFeeInBPS);
}
```

### Proof of Concept
1. Protocol has been running; `rsETHPrice = 1.05e18`, `totalETHInProtocol = 1050 ETH`, `rsethSupply = 1000`, `protocolFeeInBPS = 500` (5%).
2. 10 ETH of staking rewards arrive; `totalETHInProtocol` becomes 1060 ETH. `updateRSETHPrice()` has not been called yet.
3. Manager calls `LRTConfig.setProtocolFeeBps(1500)` (raises fee to 15%). `rsETHPrice` remains stale at `1.05e18`.
4. Anyone calls `LRTOracle.updateRSETHPrice()`.
   - `previousTVL = 1000 * 1.05e18 = 1050 ETH`
   - `rewardAmount = 1060 - 1050 = 10 ETH`
   - `protocolFeeInETH = 10 * 1500 / 10000 = 1.5 ETH` (15% applied to all 10 ETH)
   - Correct fee should have been `10 * 500 / 10000 = 0.5 ETH` (5% for the period it accrued)
5. The treasury receives 1.5 ETH worth of rsETH instead of 0.5 ETH — an extra 1 ETH of yield is taken from rsETH holders retroactively. [4](#0-3) [2](#0-1)

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

**File:** contracts/LRTConfig.sol (L196-200)
```text
    function setProtocolFeeBps(uint256 _protocolFeeInBPS) external onlyRole(LRTConstants.MANAGER) {
        if (_protocolFeeInBPS > 1500) revert ProtocolFeeExceedsLimit();
        protocolFeeInBPS = _protocolFeeInBPS;
        emit UpdateFee(_protocolFeeInBPS);
    }
```
