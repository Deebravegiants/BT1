### Title
`ethValueInWithdrawal` Permanently Overstated When Lido Finalization Rate Differs from Oracle Price at Transfer Time — (`contracts/LRTConverter.sol`)

### Summary

`LRTConverter.transferAssetFromDepositPool` records the ETH value of stETH using the oracle price at the moment of transfer. When the stETH is later unstaked and claimed via Lido, `_sendEthToDepositPool` decrements `ethValueInWithdrawal` only by the actual ETH received. If Lido's finalization rate is lower than the oracle price captured at transfer time, a permanent residual remains in `ethValueInWithdrawal`, inflating the protocol's reported TVL and rsETH price indefinitely.

---

### Finding Description

**Step 1 — `transferAssetFromDepositPool` records oracle-priced ETH value** [1](#0-0) 

`ethValueInWithdrawal` is incremented by `(_amount * lrtOracle.getAssetPrice(stETH)) / 1e18`. The oracle price is snapshotted at this moment. For 100 stETH at oracle price 1.05e18, `ethValueInWithdrawal` becomes 105e18.

**Step 2 — `unstakeStEth` submits a Lido withdrawal request** [2](#0-1) 

No change to `ethValueInWithdrawal`. The 100 stETH is locked in Lido's withdrawal queue.

**Step 3 — Lido finalizes at a lower rate**

Lido's withdrawal queue finalizes at the share rate at finalization time, which can differ from the oracle price captured in Step 1 (e.g., due to slashing events, or because the oracle reflects a market price feed that diverges from Lido's internal share rate). In the example, Lido finalizes at 1.02 ETH/stETH → 102 ETH is received.

**Step 4 — `claimStEth` calls `_sendEthToDepositPool(address(this).balance)`** [3](#0-2) [4](#0-3) 

`_sendEthToDepositPool(102e18)` executes:
```
ethValueInWithdrawal (105e18) > _amount (102e18)
→ ethValueInWithdrawal -= 102e18
→ ethValueInWithdrawal = 3e18  ← permanent residual
```

102 ETH is correctly forwarded to the deposit pool, but the 3e18 residual in `ethValueInWithdrawal` is never cleared. There is no correction path.

**Step 5 — Residual inflates rsETH price**

`getETHDistributionData` reads `ethValueInWithdrawal` directly as `ethLyingInConverter`: [5](#0-4) 

This feeds into `getTotalAssetDeposits(ETH_TOKEN)` → `_getTotalEthInProtocol()` → `_updateRsETHPrice()`: [6](#0-5) 

The phantom 3e18 is permanently included in `totalETHInProtocol`, inflating `rsETHPrice = totalETHInProtocol / rsethSupply`.

---

### Impact Explanation

`ethValueInWithdrawal` is permanently overstated by the difference between the oracle-priced value and the actual ETH received from Lido. This phantom ETH is counted in the protocol TVL on every subsequent `updateRSETHPrice()` call. New depositors receive fewer rsETH than they are entitled to because `rsETHPrice` is inflated. Existing holders benefit at the expense of new depositors. No funds are lost from the protocol, but the contract fails to deliver the promised rsETH amount to new depositors.

**Scoped impact:** Low — Contract fails to deliver promised returns, but doesn't lose value.

---

### Likelihood Explanation

This occurs in normal operator operation — no malicious intent is required. The three functions (`transferAssetFromDepositPool`, `unstakeStEth`, `claimStEth`) are the intended operational flow for converting stETH to ETH. Any divergence between the oracle price at transfer time and Lido's finalization rate (however small) produces a permanent residual. Slashing events, oracle feed lag, or market price deviations from Lido's internal share rate all create this condition. The residual accumulates across every unstake cycle.

---

### Recommendation

In `_sendEthToDepositPool`, instead of decrementing by the actual ETH amount, the function should zero out `ethValueInWithdrawal` for the completed withdrawal, or track per-request oracle-priced values and clear them exactly on claim. A simpler fix: when `claimStEth` is called, record the oracle-priced value that was committed for that specific request at `unstakeStEth` time, and subtract that committed value (not the actual ETH) from `ethValueInWithdrawal`. The actual ETH received is already correctly forwarded to the deposit pool and will be counted via `ethLyingInDepositPool`.

---

### Proof of Concept

```solidity
// Fork test (Mainnet fork, unmodified contracts)
// Setup: oracle stETH price = 1.05e18

// 1. Operator transfers 100 stETH from deposit pool to converter
lrtConverter.transferAssetFromDepositPool(stETH, 100e18);
assertEq(lrtConverter.ethValueInWithdrawal(), 105e18);

// 2. Operator submits Lido withdrawal
lrtConverter.unstakeStEth(100e18);
uint256 requestId = /* emitted from UnstakeStETHStarted event */;

// 3. Simulate Lido finalization at 1.02 ETH/stETH (e.g., post-slashing)
// withdrawalQueue.finalize(requestId, 1.02e18) — sets finalization rate to 1.02

// 4. Operator claims
lrtConverter.claimStEth(requestId, hint);
// address(lrtConverter).balance was 102e18 before _sendEthToDepositPool

// 5. Assert residual
assertEq(lrtConverter.ethValueInWithdrawal(), 3e18); // phantom ETH

// 6. Assert inflated rsETH price
lrtOracle.updateRSETHPrice();
// rsETHPrice is computed using totalETHInProtocol that includes the phantom 3e18
// New depositor receives fewer rsETH than they should
uint256 rsethMinted = lrtDepositPool.getRsETHAmountToMint(stETH, 1e18);
// rsethMinted < expected due to inflated rsETHPrice denominator
```

### Citations

**File:** contracts/LRTConverter.sol (L140-142)
```text
        ethValueInWithdrawal += (_amount * lrtOracle.getAssetPrice(_asset)) / 1e18;

        IERC20(_asset).safeTransferFrom(lrtDepositPoolAddress, address(this), _amount);
```

**File:** contracts/LRTConverter.sol (L180-183)
```text
    function claimStEth(uint256 _requestId, uint256 _hint) external nonReentrant onlyLRTOperator {
        _claimStEth(_requestId, _hint);
        _sendEthToDepositPool(address(this).balance);
    }
```

**File:** contracts/LRTConverter.sol (L252-263)
```text
    function _sendEthToDepositPool(uint256 _amount) internal {
        address lrtDepositPoolAddress = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);

        if (ethValueInWithdrawal > _amount) {
            ethValueInWithdrawal -= _amount;
        } else {
            ethValueInWithdrawal = 0;
        }
        // Send eth to deposit pool
        ILRTDepositPool(lrtDepositPoolAddress).receiveFromLRTConverter{ value: _amount }();
        emit EthTransferred(lrtDepositPoolAddress, _amount);
    }
```

**File:** contracts/unstaking-adapters/UnstakeStETH.sol (L48-57)
```text
    function _unstakeStEth(uint256 amountToUnstake) internal {
        stETH.safeIncreaseAllowance(address(withdrawalQueue), amountToUnstake);

        uint256[] memory amounts = new uint256[](1);
        amounts[0] = amountToUnstake;

        uint256[] memory requestIds = withdrawalQueue.requestWithdrawals(amounts, address(this));

        emit UnstakeStETHStarted(requestIds[0]);
    }
```

**File:** contracts/LRTDepositPool.sol (L498-500)
```text
        address lrtConverter = lrtConfig.getContract(LRTConstants.LRT_CONVERTER);
        ethLyingInConverter = ILRTConverter(lrtConverter).ethValueInWithdrawal();
    }
```

**File:** contracts/LRTOracle.sol (L231-250)
```text
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
