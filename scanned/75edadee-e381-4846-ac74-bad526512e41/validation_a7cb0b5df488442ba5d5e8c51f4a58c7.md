### Title
Emergency Aave Withdrawal Permanently Blocked by Treasury ETH Rejection — (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

`emergencyWithdrawFromAave` unconditionally calls `_collectInterestToTreasury()` before withdrawing principal. If `PROTOCOL_TREASURY` is a contract that cannot receive ETH and any interest has accrued, the hard revert inside `_collectInterestToTreasury` causes the entire emergency transaction to roll back, leaving both interest and principal frozen in Aave with no alternative extraction path.

---

### Finding Description

`emergencyWithdrawFromAave` is the sole emergency escape hatch for Aave-deposited ETH. Its execution order is:

1. Check `isAaveIntegrationEnabled` and `aaveBalance > 0`.
2. **Unconditionally** call `_collectInterestToTreasury()`.
3. Call `_withdrawFromAave(amount)`. [1](#0-0) 

Inside `_collectInterestToTreasury`, when `aaveBalance > totalETHDepositedToAave` (i.e., interest exists):

- Line 954 withdraws the interest from Aave via `aaveWETHGateway.withdrawETH(...)`.
- Line 957 attempts a raw ETH push to `PROTOCOL_TREASURY`.
- Line 958 **hard-reverts** with `TreasuryTransferFailed` if the push fails. [2](#0-1) 

Because Solidity reverts roll back all state changes, the Aave withdrawal at line 954 is also undone. The net result: the transaction reverts, nothing is withdrawn, and both principal and interest remain locked in Aave.

The same `_collectInterestToTreasury()` call appears in every other Aave exit path:

- `setAaveIntegrationEnabled(false)` — line 490
- `configureAaveIntegration` (reconfiguration branch) — line 442 [3](#0-2) 

There is no code path that withdraws from Aave while bypassing interest collection when `aaveBalance > totalETHDepositedToAave`.

---

### Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

When `PROTOCOL_TREASURY` cannot receive ETH (e.g., a multisig or DAO contract without a `receive()` function, or one that explicitly reverts on ETH receipt) and any interest has accrued:

- All three Aave exit paths revert.
- Accrued interest is permanently frozen in Aave (no extraction path exists).
- Principal is also frozen until the treasury address is updated to one that accepts ETH — making principal freezing temporary but interest freezing potentially permanent if governance is slow or unavailable.

---

### Likelihood Explanation

Treasury contracts that do not accept raw ETH are common (e.g., Gnosis Safe with no ETH fallback, DAO treasury contracts, or contracts that only accept ERC-20 tokens). The protocol does not validate that `PROTOCOL_TREASURY` can receive ETH at configuration time. Interest accrues continuously once Aave integration is active, so the precondition `aaveBalance > totalETHDepositedToAave` is met in normal operation. The PAUSER_ROLE calling `emergencyWithdrawFromAave` is the intended emergency response, making this a realistic trigger.

---

### Recommendation

Decouple interest collection from the emergency withdrawal path. Two options:

1. **Wrap `_collectInterestToTreasury()` in a try/catch inside `emergencyWithdrawFromAave`** — if interest collection fails, skip it and proceed with principal withdrawal. The interest remains in Aave (not lost) and can be collected later once the treasury issue is resolved.

2. **Add a `skipInterestCollection` boolean parameter** to `emergencyWithdrawFromAave` so the PAUSER_ROLE can bypass interest collection when the treasury is non-functional.

Either approach preserves the invariant that the emergency path always succeeds regardless of treasury state.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// ETH-rejecting treasury stub
contract RejectETHTreasury {
    receive() external payable { revert("no ETH"); }
}

// Fork test (Foundry, Aave mainnet fork)
contract EmergencyWithdrawBlockedTest is Test {
    LRTWithdrawalManager withdrawalManager; // deployed with Aave integration enabled
    RejectETHTreasury badTreasury;

    function setUp() public {
        // fork mainnet, deploy/configure withdrawalManager with Aave integration
        // deposit ETH to Aave so interest accrues
        // roll forward blocks so aaveBalance > totalETHDepositedToAave
        badTreasury = new RejectETHTreasury();
        // set PROTOCOL_TREASURY to badTreasury in lrtConfig
    }

    function test_emergencyWithdrawBlocked() public {
        // Precondition: interest has accrued
        assertGt(withdrawalManager.getAccruedInterest(), 0);

        // PAUSER_ROLE attempts emergency withdrawal
        vm.prank(pauserRole);
        vm.expectRevert(LRTWithdrawalManager.TreasuryTransferFailed.selector);
        withdrawalManager.emergencyWithdrawFromAave(type(uint256).max);

        // Both principal and interest remain in Aave
        assertGt(withdrawalManager.getAaveBalance(), 0);
    }
}
```

The test demonstrates that `emergencyWithdrawFromAave` reverts for any `amount` when the treasury rejects ETH and interest > 0, with no alternative extraction path available.

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L486-497)
```text
        if (!enabled) {
            uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
            if (aaveBalance > 0) {
                // First collect any accrued interest to treasury
                _collectInterestToTreasury();

                // Then withdraw remaining principal from Aave back to contract
                aaveBalance = aaveAWETH.balanceOf(address(this));
                if (aaveBalance > 0) {
                    _withdrawFromAave(aaveBalance);
                }
            }
```

**File:** contracts/LRTWithdrawalManager.sol (L551-563)
```text
    function emergencyWithdrawFromAave(uint256 amount) external nonReentrant onlyRole(LRTConstants.PAUSER_ROLE) {
        if (!isAaveIntegrationEnabled) revert AaveIntegrationNotEnabled();

        uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
        if (aaveBalance == 0) revert InsufficientAaveBalance();

        // First collect any accrued interest to treasury
        _collectInterestToTreasury();

        uint256 withdrawnAmount = _withdrawFromAave(amount);

        emit EmergencyWithdrawFromAave(withdrawnAmount, address(this));
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L954-958)
```text
        aaveWETHGateway.withdrawETH(aavePool, interestAmount, address(this));

        address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
        (bool sent,) = payable(treasury).call{ value: interestAmount }("");
        if (!sent) revert TreasuryTransferFailed();
```
