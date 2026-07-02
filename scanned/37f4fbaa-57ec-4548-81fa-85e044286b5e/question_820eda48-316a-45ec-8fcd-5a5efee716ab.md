[File: 'contracts/KERNEL/KERNEL.sol'] [Function: KernelDepositPool.initiateWithdrawal] Can any staker be permanently blocked from withdrawing their staked KERNEL under the precondition that maxNumberOfWithdrawalsPerUser is never set after deployment (defaults to 0 in storage), by triggering the call sequence initialize() -> stake(amount) -> initiateWithdrawal(amount) -> WithdrawalLimitReached revert (because userWithdrawalIds[msg.sender].length >= 0 is always true), violating the invariant that staked KERNEL must always be withdrawable by the depositor, causing scoped impact: permanent freezing of staked KERNEL yield and principal? Proof idea: deploy KernelDepositPool without calling setMaxNumberOfWithdrawalsPerUser; assert initiateWithdrawal reverts for any staker; assert setMaxNumberOfWithdrawalsPerUser(0) also reverts due to InvalidMaxNumberOfWithdrawalsPerUser, confirming the only

### Citations

**File:** contracts/KERNEL/KERNEL.sol (L1-11)
```text
// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.27;

import { ERC20 } from
