### Title
Missing `rsETHPrice` update prior to `protocolFeeInBPS` change leads to incorrect protocol fee computation — (`File: contracts/LRTOracle.sol`)

### Summary

`LRTConfig.setProtocolFeeBps()` updates `protocolFeeInBPS` without first calling `LRTOracle.updateRSETHPrice()`. Because `protocolFeeInBPS` determines the percentage of accumulated rewards taken as a protocol fee, changing it without first settling the pending reward period causes the new rate to be retroactively applied to rewards that accrued under the old rate.

### Finding Description

In `LRTOracle._updateRsETHPrice()`, the protocol fee is computed as a percentage of the reward that has accumulated since the last price update:

```solidity
// contracts/LRTOracle.sol lines 244-246
if (!protocolPaused && totalETHInProtocol > previousTVL) {
    uint256 rewardAmount = totalETHInProtocol - previousTVL;
    protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
}
```

`previousTVL` is reconstructed as `rsethSupply * rsETHPrice` (the last stored price), so `rewardAmount` captures all ETH yield that has accrued since the last call to `updateRSETHPrice()`. [1](#0-0) 

`protocolFeeInBPS` is updated in `LRTConfig.setProtocolFeeBps()` with no prior settlement of the pending reward period:

```solidity
// contracts/LRTConfig.sol lines 196-200
function setProtocolFeeBps(uint256 _protocolFeeInBPS) external onlyRole(LRTConstants.MANAGER) {
    if (_protocolFeeInBPS > 1500) revert ProtocolFeeExceedsLimit();
    protocolFeeInBPS = _protocolFeeInBPS;
    emit UpdateFee(_protocolFeeInBPS);
}
``` [2](#0-1) 

This creates the following exploitable sequence:

1. The protocol has been running with `protocolFeeInBPS = 500` (5%). EigenLayer staking rewards accumulate, growing `totalETHInProtocol` by, say, 100 ETH above `previousTVL`. No one has called `updateRSETHPrice()` yet.
2. The manager calls `setProtocolFeeBps(1500)` (15%). The 100 ETH of accumulated rewards are not settled — `rsETHPrice` is not updated.
3. The next call to `updateRSETHPrice()` (callable by anyone) applies the new 15% rate to the entire 100 ETH, charging 15 ETH as protocol fee instead of the correct 5 ETH. The 10 ETH difference is silently redirected from rsETH holders to the treasury.

The reverse scenario (fee decrease) causes the treasury to receive less fee than it earned under the old rate.

### Impact Explanation

**High — Theft of unclaimed yield.**

When `protocolFeeInBPS` is increased before `updateRSETHPrice()` is called, rsETH holders lose yield that accrued while the lower fee was in effect. The excess fee is minted as rsETH to the treasury at the expense of existing holders' share value. The magnitude scales with the size of accumulated rewards and the magnitude of the fee change. The maximum fee is capped at 1500 BPS (15%), so the worst-case delta per update cycle is 15% of all accumulated rewards since the last price update. [3](#0-2) 

### Likelihood Explanation

**Medium.** Fee rate changes are routine governance operations. The vulnerability is triggered by the normal, non-malicious act of updating `protocolFeeInBPS`. The impact is proportional to the time elapsed since the last `updateRSETHPrice()` call and the size of the fee change. Protocols with infrequent oracle updates (e.g., once per day) and large TVL are most exposed. [4](#0-3) 

### Recommendation

Call `updateRSETHPrice()` (or its internal equivalent `_updateRsETHPrice()`) inside `setProtocolFeeBps()` before updating the fee, so that all rewards accumulated under the old rate are settled first:

```solidity
function setProtocolFeeBps(uint256 _protocolFeeInBPS) external onlyRole(LRTConstants.MANAGER) {
    if (_protocolFeeInBPS > 1500) revert ProtocolFeeExceedsLimit();
    // Settle pending rewards at the current fee rate before changing it
    ILRTOracle(contractMap[LRTConstants.LRT_ORACLE]).updateRSETHPrice();
    protocolFeeInBPS = _protocolFeeInBPS;
    emit UpdateFee(_protocolFeeInBPS);
}
```

Alternatively, enforce the settlement inside `LRTOracle` by exposing a privileged `updateRSETHPriceAndSetFee()` function that atomically settles then updates the fee. [5](#0-4) 

### Proof of Concept

**Setup:**
- `rsETHPrice = 1.05e18` (stored), `rsethSupply = 1,000,000e18`
- `previousTVL = 1,050,000e18` ETH
- `protocolFeeInBPS = 500` (5%)
- EigenLayer rewards cause `totalETHInProtocol = 1,051,000e18` (1,000 ETH reward accrued)

**Step 1:** Manager calls `LRTConfig.setProtocolFeeBps(1500)`. No price update occurs. [2](#0-1) 

**Step 2:** Any user (or keeper) calls `LRTOracle.updateRSETHPrice()`. [4](#0-3) 

**Step 3:** Inside `_updateRsETHPrice()`:
- `rewardAmount = 1,051,000e18 - 1,050,000e18 = 1,000e18`
- `protocolFeeInETH = 1,000e18 * 1500 / 10_000 = 150e18` ← uses new 15% rate
- Correct fee should have been `1,000e18 * 500 / 10_000 = 50e18`
- **100 ETH of yield is incorrectly redirected from rsETH holders to the treasury.** [6](#0-5)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L228-250)
```text
        uint256 previousPrice = rsETHPrice;

        // get total ETH in the protocol (normalized to 1e18)
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

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
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
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
