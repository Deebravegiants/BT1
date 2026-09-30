# [H] 5.2.1 DOS attack by delegating tokens atMAX_DELEGATES = 1024.

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** VotingEscrow.sol#L
**Description:** Any user can delegate the balance of the locked NFT amount to anyone by callingdelegate. As the
delegated tokens are maintained in an array that's vulnerable to DOS attack, theVotingEscrowhas a safety check
ofMAX_DELEGATES = 1024preventing an address from having a huge array. Given the current implementation,
any user with 1024 delegated tokens takes approximately 23M gas totransfer/burn/minta token. However, the
current gas limit of the op chain is 15M. (ref: Op-scan)

- The currentvotingEscrowhas a limit ofMAX_DELEGATES=1024.it's approx 23M to transfer/withdraw a token
    when there are 1024 delegated voting on a token.
- It's cheaper to delegate from an address with a shorter token list to an address with a longer token list. =>
    If someone trying to attack a victim's address by creating a new address, a new lock, and delegating to the
    victim. By the time the attacker hit the gas limit, the victim can not withdraw/transfer/delegate.
**Recommendation:** There's currently no clear hard limit of block size in OP's spec. There's also a chance the OP's
sequencer will include a jumbo tx if funds get locked because of out of gas. Nevertheless, there's no precedent
example of such cases and it's not a desirable situation for users to deal with the risks. Hence recommend to take
to:
1. Adjust theMAX_DELEGATES=1024to 128 ;
2. Give an option for users to opt-out/opt-in. Users will only accept the delegated tokens if theyopt-in; or users
can opt-out to refuse any uncommissioned delegated tokens.
Also, recommend adding the following test inVotingEscrow.t.sol
contract VotingEscrowTest is BaseTest {
function testDelegateLimitAttack() public {
vm.prank(address(owner));
VELO.transfer(address(this), TOKEN_1M);
VELO.approve(address(escrow), type(uint256).max);
uint tokenId = escrow.createLock(TOKEN_1, 7 days);
for(uint256 i = 0; i < escrow.MAX_DELEGATES() - 1; i++) {
vm.roll(block.number + 1);
vm.warp(block.timestamp + 2);
address fakeAccount = address(uint160(420 + i));
VELO.transfer(fakeAccount, 1 ether);
vm.startPrank(fakeAccount);
VELO.approve(address(escrow), type(uint256).max);
escrow.createLock(1 ether, MAXTIME);
escrow.delegate(address(this));
vm.stopPrank();
}
vm.roll(block.number + 1);
vm.warp(block.timestamp + 7 days);
uint initialGas = gasleft();
escrow.withdraw(tokenId);
uint gasUsed = initialGas - gasleft();
// @audit: setting 10_000_000 to demonstrate the issue. 2~3M gas limit would be a safer range.
assertLt(gasUsed, 10_000_000);
}
}

**Velodrome:** Fixed in commit 0b47fe. Delegation was reworked to use static balances so that it would no longer
have a limit. This required the introduction of permanent locks which are locks that do not decay.
**Spearbit:** Verified
