### Title
Permanent Freezing of KERNEL Tokens Due to Initiator-Locked Withdrawal Claim — (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
`KernelDepositPool.claimWithdrawal` enforces that only the exact address that called `initiateWithdrawal` can ever claim the resulting withdrawal. There is no admin override, no recipient parameter, and no recovery path. If the initiating address becomes inaccessible after the withdrawal is queued — a realistic scenario for smart-contract wallets (multisigs, DAO treasuries, proxy vaults) that are migrated or redeployed — the staked KERNEL tokens are permanently frozen inside the contract.

### Finding Description
`initiateWithdrawal` writes `msg.sender` directly into the `Withdrawal` struct:

```solidity
// contracts/KERNEL/KernelDepositPool.sol:332-334
withdrawals[withdrawalId] = Withdrawal({
    user: msg.sender, amount: _amount, unlockTime: unlockTime, ...
});
```

`claimWithdrawal` then hard-gates on that stored address:

```solidity
// contracts/KERNEL/KernelDepositPool.sol:351-353
if (withdrawal.user != msg.sender) {
    revert NotYourWithdrawal();
}
```

Tokens are sent to `msg.sender` (line 376), not to `withdrawal.user`, so the check is both a gate and the sole delivery path. No function in the contract allows an admin, operator, or any third party to claim on behalf of a different address, nor is there any mechanism to update `withdrawal.user` after the fact.

Contrast this with `LRTWithdrawalManager`, which provides `completeWithdrawalForUser` (an operator-callable override) as a recovery path. `KernelDepositPool` has no equivalent.

### Impact Explanation
If the address stored in `withdrawal.user` can no longer sign transactions — because a multisig was migrated to a new deployment, a proxy vault was replaced, or a DAO treasury contract was upgraded — the KERNEL tokens committed to that withdrawal are permanently locked in the contract with no recovery path. This constitutes **permanent freezing of funds** (Critical).

### Likelihood Explanation
The scenario is realistic for any protocol-level or DAO-level staker using a smart-contract wallet. Multisig migrations (e.g., Gnosis Safe redeployment to a new address) and proxy vault replacements are routine operational events. A staker that queues a withdrawal before such a migration and completes the migration before the unlock time expires will find their tokens irrecoverable. Likelihood is **Low-Medium** given the operational context of KERNEL stakers.

### Recommendation
- **Short term**: Add an operator-callable `claimWithdrawalForUser(uint256 _withdrawalId, address _user)` that bypasses the `msg.sender` check and transfers tokens to `withdrawal.user`, mirroring `LRTWithdrawalManager.completeWithdrawalForUser`.
- **Long term**: Allow the initiating address to designate a separate `recipient` at claim time, or provide an admin function to update `withdrawal.user` in case of address migration, with appropriate access controls and event emission.

### Proof of Concept
1. Alice (a Gnosis Safe multisig at address `0xAlice`) calls `initiateWithdrawal(1_000e18)`. The contract stores `withdrawal.user = 0xAlice`.
2. Alice's DAO migrates to a new multisig deployment at `0xBob`.
3. After `unlockTime` passes, `0xBob` calls `claimWithdrawal(withdrawalId)`.
4. The check `withdrawal.user (0xAlice) != msg.sender (0xBob)` triggers `revert NotYourWithdrawal()`.
5. `0xAlice` is no longer operational. The 1,000 KERNEL tokens are permanently frozen. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L332-334)
```text
        withdrawals[withdrawalId] = Withdrawal({
            user: msg.sender, amount: _amount, unlockTime: unlockTime, claimed: false, withdrawalId: withdrawalId
        });
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L344-353)
```text
    function claimWithdrawal(uint256 _withdrawalId) external nonReentrant {
        Withdrawal storage withdrawal = withdrawals[_withdrawalId];

        if (withdrawal.user == address(0)) {
            revert WithdrawalDoesNotExist();
        }

        if (withdrawal.user != msg.sender) {
            revert NotYourWithdrawal();
        }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L374-379)
```text

        // Transfer the KERNEL tokens from contract to user
        kernelToken.safeTransfer(msg.sender, withdrawal.amount);

        emit WithdrawalClaimed(msg.sender, withdrawal.amount, _withdrawalId);
    }
```
