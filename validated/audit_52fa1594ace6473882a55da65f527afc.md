### Title
Uninitialized `maxNumberOfWithdrawalsPerUser` Permanently Blocks Withdrawals Until Admin Intervention - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
`initialize()` never sets `maxNumberOfWithdrawalsPerUser`, leaving it at the Solidity default of `0`. The guard in `initiateWithdrawal()` compares `userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser`, which evaluates to `0 >= 0 == true` for every caller, causing an unconditional revert with `WithdrawalLimitReached`. All staked KERNEL tokens are frozen until the admin separately calls `setMaxNumberOfWithdrawalsPerUser`.

### Finding Description
`initialize()` sets `kernelToken`, `rewardsToken`, and the admin role, but never assigns `maxNumberOfWithdrawalsPerUser`: [1](#0-0) 

`setMaxNumberOfWithdrawalsPerUser` is a standalone admin function, entirely decoupled from initialization: [2](#0-1) 

`initiateWithdrawal` enforces the limit before any state change: [3](#0-2) 

Because `maxNumberOfWithdrawalsPerUser == 0` after `initialize()`, the condition `userWithdrawalIds[msg.sender].length >= 0` is trivially true for every address (a `uint256` is always `>= 0`), so every call to `initiateWithdrawal` reverts unconditionally.

### Impact Explanation
All KERNEL tokens staked via `stake()` or `stakeFor()` are inaccessible until the admin calls `setMaxNumberOfWithdrawalsPerUser`. There is no alternative withdrawal path in the contract. This constitutes **temporary freezing of funds** (Medium). [4](#0-3) 

### Likelihood Explanation
Any deployment that calls `initialize()` without immediately following it with `setMaxNumberOfWithdrawalsPerUser` triggers this state. There is no on-chain enforcement requiring the admin to call the setter before users stake. The window between deployment and the admin setter call — which could be hours, days, or indefinite if overlooked — freezes all staked funds.

### Recommendation
Set a safe default for `maxNumberOfWithdrawalsPerUser` inside `initialize()`, e.g.:

```solidity
maxNumberOfWithdrawalsPerUser = MAX_WITHDRAWALS_PER_USER; // 100
```

This ensures the contract is functional immediately after deployment while still allowing the admin to tighten the limit later.

### Proof of Concept

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

Running this test against the unmodified contract confirms that `initiateWithdrawal` reverts with `WithdrawalLimitReached` immediately after `initialize()`, freezing the staked balance.

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L259-271)
```text
    function initialize(address _admin, address _kernelToken, address _rewardToken) external initializer {
        UtilLib.checkNonZeroAddress(_admin);
        UtilLib.checkNonZeroAddress(_kernelToken);
        UtilLib.checkNonZeroAddress(_rewardToken);

        __AccessControl_init();
        __ReentrancyGuard_init();

        _setupRole(DEFAULT_ADMIN_ROLE, _admin);

        kernelToken = IERC20(_kernelToken);
        rewardsToken = IERC20(_rewardToken);
    }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L281-289)
```text
    function stake(uint256 _amount) external nonReentrant updateReward(msg.sender) {
        if (_amount == 0) revert AmountZero();

        balanceOf[msg.sender] += _amount;
        totalKernelStaked += _amount;
        kernelToken.safeTransferFrom(msg.sender, address(this), _amount);

        emit Staked(msg.sender, _amount);
    }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L323-323)
```text
        if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L610-620)
```text
    function setMaxNumberOfWithdrawalsPerUser(uint256 _maxNumberOfWithdrawalsPerUser)
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        if (_maxNumberOfWithdrawalsPerUser == 0 || _maxNumberOfWithdrawalsPerUser > MAX_WITHDRAWALS_PER_USER) {
            revert InvalidMaxNumberOfWithdrawalsPerUser();
        }

        maxNumberOfWithdrawalsPerUser = _maxNumberOfWithdrawalsPerUser;
        emit MaxNumberOfWithdrawalsPerUserUpdated(_maxNumberOfWithdrawalsPerUser);
    }
```
