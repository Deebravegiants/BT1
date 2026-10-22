# [M] Fr Resolve users

## Summary
Severity: Medium
Contest weight: 0.0000
Dataset id: 23308
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When resolving a user to migrate his tokens, lock progress, and payouts from an address to a new address, the balance of ChildToken of the oldAddress is transferred by directly calling the `super._transfer`, which bypasses the overrides of the `super._transfer`. Calling `super._transfer` bypasses a protection that returns the execution early when transferring a zero value. This allows the execution to reach `ChildToken::_update()` with a balance of 0 for the from account and a transfer of zero value. As a result, the `totalInvestors` counter will be decremented, because the condition evaluating whether the sender is zeroing out their balance will be met.

```solidity
//ChildToken.sol//
function resolveUser(address oldAddress, address newAddress) external nonReentrant restricted {
    ...
    super._transfer(oldAddress, newAddress, value); // tokens already locked with _newAccountSameLocks,!
}
function _update(
    address from,
    address to,
    uint256 value
) internal override {
    if (from != address(0) && balanceOf(from) - value == 0) --totalInvestors;
    if (to != address(0) && balanceOf(to) == 0) ++totalInvestors;
    ...
}
```

The previous behavior when resolving a user who has no balance allows for legitimate executions to determine users to be griefed and force the `totalInvestors` counter to be decremented twice. One for the frontran transaction, which transfers all the `oldAddress` tokens (because the sender is zeroing out their balance). Again, when the transaction calling `ChildToken::resolveUser` is executed and resolves the user with a zero balance (as explained above), this will also cause `investorBalance` to be decremented.

Impact: The `totalInvestor` counter is decremented twice, which causes the system to inaccurately track the actual number of investors in the system. This issue can cause transfers of other investors to fall into DoS when transferring all their balances (given sufficient manipulations of the `totalInvestor` counter). However, thanks to the lock‑up periods, the likelihood of reaching a DoS state is low.

## Proof of Concept
```solidity
function test_resolveUser_FrontRanHijacks_totalInvestorCounter() public {
    address oldUser = getDomesticUser(1);
    address newUser = getDomesticUser(2);
    address extraInvestor = getDomesticUser(3);
    centralTokenProxy.mint(address(this), uint64(1));
    centralTokenProxy.dynamicTransfer(extraInvestor, 1);
    // Seed: old user has 3 tokens (locked by default on mint)
    centralTokenProxy.mint(address(this), uint64(3));
    centralTokenProxy.dynamicTransfer(oldUser, 3);
    assertEq(d_childTokenProxy.balanceOf(oldUser), 3);
    // Distribute payout via PaymentSettler -> Central -> Child
    IERC20(address(stableCoin)).approve(address(paySettlerProxy), type(uint256).max);
    paySettlerProxy.distributePayment(address(centralTokenProxy), address(this), 300); // 300 USD(6)
    total,!
    30
    assertEq(d_childTokenProxy.totalInvestors(), 2);
    uint32 DEFAULT_LOCK_TIME = 365 days;
    vm.warp(block.timestamp + DEFAULT_LOCK_TIME);
    //@audit-info => `oldUser` frontruns `resolveUser()` and transfers all of his balance!
    vm.prank(oldUser);
    d_childTokenProxy.transfer(newUser, 3);
    //@audit-info => Doesn't revert even though `oldUser` has 0 balance
    // Resolve: move state to newUser (already allowlisted + signed in base)
    d_childTokenProxy.resolveUser(oldUser, newUser);
    //@audit-issue => Only 1 investor when in reality are 2 (newUser and extraInvestor)
    assertEq(d_childTokenProxy.totalInvestors(), 1);
    //@audit-info => newUser transfers all his tokens to extraInvestor - totalInvestors shrinks
    vm.warp(block.timestamp + DEFAULT_LOCK_TIME);
    vm.prank(newUser);
    d_childTokenProxy.transfer(extraInvestor, 3);
    assertEq(d_childTokenProxy.totalInvestors(), 0);
    //@audit-issue => underflow because totalInvestors is 0 and extraInvestor is transferring all of
    // his balance,!
    vm.warp(block.timestamp + DEFAULT_LOCK_TIME);
    vm.prank(extraInvestor);
    vm.expectRevert();
    d_childTokenProxy.transfer(newUser, 4);
}
```

## Recommendation
Consider adding a check to validate if the `oldAddress` `balanceOf` ChildToken is 0, if so, revert the tx.
