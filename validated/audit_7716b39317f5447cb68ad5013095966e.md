### Title
Protocol Charges Fees on Slashing Recovery Using Wrong Price Baseline — (File: `contracts/LRTOracle.sol`)

### Summary
In `LRTOracle._updateRsETHPrice()`, the fee baseline is `rsETHPrice` (the last stored price) rather than `highestRsethPrice` (the all-time high). After a slashing event drops the price below `highestRsethPrice`, any subsequent recovery is treated as "new yield" and subjected to protocol fees, even though the price has not yet returned to its previous peak. rsETH holders who already absorbed the slashing loss are further penalized by having their recovery gains partially extracted as protocol fees.

---

### Finding Description

`_updateRsETHPrice()` computes `previousTVL` as `rsethSupply * rsETHPrice` at line 234. The protocol fee is charged whenever `totalETHInProtocol > previousTVL`. After a slashing event:

1. Price drops from `P_high` to `P_low`; `rsETHPrice` is stored as `P_low`; `highestRsethPrice` remains `P_high`.
2. Protocol may pause (downside protection), then unpause.
3. Yield accrues; price recovers to `P_mid` where `P_low < P_mid < P_high`.
4. `previousTVL = rsethSupply * P_low` (uses stale `rsETHPrice`).
5. `rewardAmount = rsethSupply * (P_mid - P_low)` — treated as new yield.
6. Protocol fee is charged on this recovery amount.

The correct baseline should be `highestRsethPrice` (`P_high`), so that fees are only charged on genuine new yield above the previous peak. The `highestRsethPrice` variable already exists and is used for downside protection (lines 270–291), but is not used as the fee baseline — an inconsistency that constitutes the root cause.

The vulnerable lines are: [1](#0-0) 

```solidity
// calculate previousTVL using rsethSupply multiplied by rsETHPrice  ← wrong baseline
uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);
...
if (!protocolPaused && totalETHInProtocol > previousTVL) {
    uint256 rewardAmount = totalETHInProtocol - previousTVL;
    protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
}
```

`highestRsethPrice` is tracked and updated correctly: [2](#0-1) 

but is never consulted when deciding whether a fee is owed.

---

### Impact Explanation

rsETH holders who suffered a slashing loss have their recovery gains partially extracted as protocol fees. Example with a 10% fee rate:

- Price drops from 1.1 → 1.0 ETH/rsETH (slashing); `rsETHPrice = 1.0`, `highestRsethPrice = 1.1`.
- Price recovers to 1.05 ETH/rsETH.
- `rewardAmount = rsethSupply × 0.05 ETH` — treated as new yield.
- `protocolFeeInETH = rsethSupply × 0.005 ETH` minted to treasury.
- rsETH holders, who already lost 0.1 ETH/rsETH to slashing, now lose an additional fee on their 0.05 ETH/rsETH recovery and can never fully recover their slashing loss through normal yield accrual.

**Impact: High — Theft of unclaimed yield.**

---

### Likelihood Explanation

EigenLayer slashing is a realistic and expected event for a restaking protocol. The protocol already tracks `highestRsethPrice` specifically to handle price-drop scenarios, confirming the scenario is anticipated. Any slashing event followed by partial recovery triggers this bug without any special conditions. The public `updateRSETHPrice()` function can be called by anyone when the protocol is unpaused, so no privileged access is required to trigger the incorrect fee extraction. [3](#0-2) 

**Likelihood: Medium.**

---

### Recommendation

Replace `rsETHPrice` with `highestRsethPrice` as the fee baseline so that fees are only charged on genuine new yield above the previous peak:

```solidity
// Before (buggy):
uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);

// After (fixed):
uint256 highWaterMark = highestRsethPrice > rsETHPrice ? highestRsethPrice : rsETHPrice;
uint256 previousTVL = rsethSupply.mulWad(highWaterMark);
```

Since `highestRsethPrice >= rsETHPrice` is invariant after initialization, this simplifies to:

```solidity
uint256 previousTVL = rsethSupply.mulWad(highestRsethPrice);
```

---

### Proof of Concept

1. Protocol starts: `rsETHPrice = highestRsethPrice = 1.1e18`.
2. Slashing event: `totalETHInProtocol` drops; `updateRSETHPrice()` is called; `rsETHPrice` is stored as `1.0e18`; `highestRsethPrice` remains `1.1e18` (unchanged, per line 294).
3. Protocol unpauses; yield accrues; `totalETHInProtocol` rises to `rsethSupply × 1.05e18`.
4. Any caller invokes `updateRSETHPrice()`:
   - `previousTVL = rsethSupply × 1.0e18` (uses `rsETHPrice`, not `highestRsethPrice`)
   - `rewardAmount = rsethSupply × 0.05e18`
   - `protocolFeeInETH = rsethSupply × 0.05e18 × feeBPS / 10_000`
   - Fee rsETH is minted to treasury at line 306.
5. rsETH holders, who already lost 0.1 ETH/rsETH to slashing, now lose an additional fee on their 0.05 ETH/rsETH recovery.
6. With `highestRsethPrice = 1.1e18` as the correct baseline: `previousTVL = rsethSupply × 1.1e18 > totalETHInProtocol`, so `rewardAmount = 0` and no fee is taken — the correct behavior. [4](#0-3) 

This is the direct analog of the original bug: using the wrong reference price (`rsETHPrice` instead of `highestRsethPrice`) causes incorrect fee extraction during recovery from negative growth, mirroring the use of `_initialSharePrice` instead of `_openSharePrice` in the Hyperdrive finding.

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L228-251)
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

**File:** contracts/LRTOracle.sol (L293-296)
```text
        // update highest price if new price exceeds it
        if (newRsETHPrice > highestRsethPrice) {
            highestRsethPrice = newRsETHPrice;
        }
```
