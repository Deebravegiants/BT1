The code confirms the claim. `initialize()` at L259-271 never assigns `maxNumberOfWithdrawalsPerUser`, leaving it at the Solidity default of `0`. The guard at L323 is `userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser`, which evaluates to `0 >= 0 == true` for every first-time caller, causing an unconditional revert. `setMaxNumberOfWithdrawalsPerUser()` at L610-620 is the only setter and is admin-gated. The finding is valid.

---

Audit Report

## Title
Uninitialized `maxNumberOfWithdrawalsPerUser` Blocks All Withdrawals After Deployment - (File: contracts/KERNEL/KernelDepositPool.sol)

## Summary
`initialize()` never sets `maxNumberOfWithdrawalsPerUser`, leaving it at the Solidity default of `0`. The guard in `initiateWithdrawal()` checks `userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser`, which is trivially `true` for every caller since any `uint256` is `>= 0`. Every call to `initiateWithdrawal()` reverts with `WithdrawalLimitReached`, freezing all staked KERNEL tokens until the admin separately calls `setMaxNumberOfWithdrawalsPerUser`.

## Finding Description
`initialize()` sets `kernelToken`, `rewardsToken`, and the admin role, but never assigns `maxNumberOfWithdrawalsPerUser`:

```solidity
// L259-271: no assignment to maxNumberOfWithdrawalsPerUser
function initialize(address _admin, address _kernelToken, address _rewardToken) external initializer {
    ...
    kernelToken = IERC20(_kernelToken);
    rewardsToken = IERC20(_rewardToken);
}
```

The state variable defaults to `0`:

```solidity
// L108
uint256 public maxNumberOfWithdrawalsPerUser;
```

`initiateWithdrawal()` enforces the limit before any state change:

```solidity
// L323
if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();
```

With `maxNumberOfWithdrawalsPerUser == 0`, the expression `uint256(0) >= uint256(0)` is always `true`, so every invocation reverts. The only remedy is the admin calling `setMaxNumberOfWithdrawalsPerUser`, which explicitly rejects `0` as a value and is entirely decoupled from initialization:

```solidity
// L614
if (_maxNumberOfWithdrawalsPerUser == 0 || _maxNumberOfWithdrawalsPerUser > MAX_WITHDRAWALS_PER_USER) {
    revert InvalidMaxNumberOfWithdrawalsPerUser();
}
```

There is no alternative withdrawal path in the contract.

## Impact Explanation
All KERNEL tokens staked via `stake()` or `stakeFor()` are inaccessible to users until the admin calls `setMaxNumberOfWithdrawalsPerUser`. This constitutes **temporary freezing of funds** (Medium), matching the allowed impact scope.

## Likelihood Explanation
Any deployment that calls `initialize()` without immediately following it with `setMaxNumberOfWithdrawalsPerUser` triggers this state. There is no on-chain enforcement requiring the admin to call the setter before users stake. The window between deployment and the admin setter call — which could be hours, days, or indefinite if overlooked — freezes all staked funds for all users.

## Recommendation
Set a safe default for `maxNumberOfWithdrawalsPerUser` inside `initialize()`:

```solidity
maxNumberOfWithdrawalsPerUser = MAX_WITHDRAWALS_PER_USER; // 100
```

This ensures the contract is functional immediately after deployment while still allowing the admin to adjust the limit later via `setMaxNumberOfWithdrawalsPerUser`.

## Proof of Concept
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.27;

import "forge-std/Test.sol";
import "contracts/KERNEL/KernelDepositPool.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MockERC20 is ERC20 {
    constructor() ERC20("Mock", "MCK") { _mint(msg.sender, 1e24); }
}

contract KernelDepositPoolTest is Test {
    KernelDepositPool pool;
    MockERC20 kernel;
    MockERC20 reward;
    address user = address(0xBEEF);

    function setUp() public {
        kernel = new MockERC20();
        reward = new MockERC20();
        pool = new KernelDepositPool();
        // initialize() — setMaxNumberOfWithdrawalsPerUser is NOT called
        pool.initialize(address(this), address(kernel), address(reward));
        kernel.transfer(user, 1e18);
    }

    function testWithdrawalFrozenWhenMaxNotSet() public {
        vm.startPrank(user);
        kernel.approve(address(pool), 1e18);
        pool.stake(1e18);
        // maxNumberOfWithdrawalsPerUser == 0, so 0 >= 0 is true → always reverts
        vm.expectRevert(KernelDepositPool.WithdrawalLimitReached.selector);
        pool.initiateWithdrawal(1e18);
        vm.stopPrank();
    }
}
```