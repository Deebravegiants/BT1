### Title
Missing `updateRSETHPrice()` Before `protocolFeeInBPS` Update Causes Retroactive Fee Application on Accrued Rewards - (File: contracts/LRTConfig.sol)

### Summary
`LRTConfig.setProtocolFeeBps()` updates `protocolFeeInBPS` without first settling pending rewards via `LRTOracle.updateRSETHPrice()`. Because `_updateRsETHPrice()` reads the current `protocolFeeInBPS` at call time and applies it to all rewards accrued since the last price update, a fee change retroactively taxes already-accrued yield at the new rate, causing rsETH holders to lose yield when the fee is raised.

### Finding Description
`LRTOracle._updateRsETHPrice()` computes the protocol fee by comparing the current TVL against the previously stored `rsETHPrice` to derive `rewardAmount`, then applies the live `lrtConfig.protocolFeeInBPS()` to that entire reward window:

```solidity
// contracts/LRTOracle.sol lines 244-246
if (!protocolPaused && totalETHInProtocol > previousTVL) {
    uint256 rewardAmount = totalETHInProtocol - previousTVL;
    protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
}
```

`rewardAmount` represents all rewards that accrued since the last `updateRSETHPrice()` call — potentially spanning many hours or days. The fee rate applied to this entire window is whatever `protocolFeeInBPS` is at the moment `updateRSETHPrice()` is called, not the rate that was in effect when the rewards were earned.

`LRTConfig.setProtocolFeeBps()` makes no call to settle pending rewards before changing the rate:

```solidity
// contracts/LRTConfig.sol lines 196-200
function setProtocolFeeBps(uint256 _protocolFeeInBPS) external onlyRole(LRTConstants.MANAGER) {
    if (_protocolFeeInBPS > 1500) revert ProtocolFeeExceedsLimit();
    protocolFeeInBPS = _protocolFeeInBPS;
    emit UpdateFee(_protocolFeeInBPS);
}
```

There is no `updateRSETHPrice()` call before or after the assignment, and no on-chain enforcement requiring the caller to settle first.

### Impact Explanation
When `protocolFeeInBPS` is raised (e.g., from 500 bps to 1500 bps), the next `updateRSETHPrice()` call applies the new higher rate to the entire unsettled reward window. rsETH holders bear the cost: the new rsETH price is lower than it should be, permanently diluting their share of the TVL. The excess fee is minted as rsETH to the treasury at the expense of existing holders.

Concretely: if 100 ETH in rewards accrued under a 5% fee but `updateRSETHPrice()` is called after the fee is raised to 15%, the protocol takes 15 ETH instead of 5 ETH — a 10 ETH loss of yield for rsETH holders. This matches the **High** impact category: theft of unclaimed yield.

### Likelihood Explanation
`setProtocolFeeBps()` is a routine governance action callable by the `MANAGER` role. The protocol does not document any requirement to call `updateRSETHPrice()` first, and there is no on-chain enforcement. `updateRSETHPrice()` is a public function that can be called by anyone, but there is no guarantee it will be called immediately before a fee change. The window between price updates can be hours long (the oracle is not called on every block). This is a realistic scenario with every fee adjustment.

### Recommendation
Call `updateRSETHPrice()` (or an equivalent internal settlement) at the start of `setProtocolFeeBps()` before writing the new fee value, analogous to how lending protocols call `accrueInterest()` before changing rate models:

```solidity
function setProtocolFeeBps(uint256 _protocolFeeInBPS) external onlyRole(LRTConstants.MANAGER) {
    if (_protocolFeeInBPS > 1500) revert ProtocolFeeExceedsLimit();
    // Settle pending rewards at the current fee rate before changing it
    ILRTOracle(contractMap[LRTConstants.LRT_ORACLE]).updateRSETHPrice();
    protocolFeeInBPS = _protocolFeeInBPS;
    emit UpdateFee(_protocolFeeInBPS);
}
```

### Proof of Concept

**Setup:**
- `rsETHPrice` = 1.05e18 (last settled price)
- `rsethSupply` = 1000 rsETH → `previousTVL` = 1050 ETH
- `totalETHInProtocol` = 1150 ETH (100 ETH in rewards accrued since last update)
- Current `protocolFeeInBPS` = 500 (5%)

**Step 1 — MANAGER raises fee without settling:**
```
LRTConfig.setProtocolFeeBps(1500)  // raises to 15%
// No updateRSETHPrice() called
```

**Step 2 — Anyone calls `updateRSETHPrice()`:**
```
rewardAmount = 1150 ETH - 1050 ETH = 100 ETH
protocolFeeInETH = 100 ETH * 1500 / 10_000 = 15 ETH   ← new rate applied to old rewards
newRsETHPrice = (1150 - 15) / 1000 = 1.135 ETH/rsETH
```

**Expected (if settled before fee change):**
```
protocolFeeInETH = 100 ETH * 500 / 10_000 = 5 ETH
newRsETHPrice = (1150 - 5) / 1000 = 1.145 ETH/rsETH
```

**Loss to rsETH holders:** 0.010 ETH per rsETH × 1000 rsETH = **10 ETH of yield stolen** from holders and redirected to the treasury. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/LRTConfig.sol (L196-200)
```text
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

**File:** contracts/LRTOracle.sol (L244-246)
```text
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
```

**File:** contracts/LRTOracle.sol (L298-313)
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
        } else {
            _checkAndUpdateDailyFeeMintLimit(0);
        }

        rsETHPrice = newRsETHPrice;
```
