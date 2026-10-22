# [H] Voters from VotingEscrow can vote infinite times in vote _for_ gauge_weights

## Summary
Severity: High
Contest weight: 0.7144
Dataset id: 19207
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an unlimited vote‑inflation flaw in the interaction between a token‑locking escrow contract and a gauge controller that determines reward distribution. The escrow contract lets a token holder lock assets and optionally delegate the associated voting power to another address. The gauge controller reads the voting power of a voter by querying the current timestamp (or the current block) instead of a snapshot taken a fixed number of blocks in the past. Because the snapshot is taken at the moment of each call, a user can vote for a gauge, immediately delegate the same voting power to a fresh address, and have that address cast another vote using the same underlying lock. By repeating the delegate‑vote cycle arbitrarily many times, the attacker can multiply the effective weight of a single lock by the number of delegations performed. The inflated weight is then used by downstream contracts such as a lending ledger to calculate token rewards, allowing the attacker to claim far more tokens than their actual locked stake justifies. The issue manifests whenever a lock exists, the delegate function is available, and the gauge controller does not enforce a voting window or a historical snapshot. It affects all participants that rely on gauge weights for fair reward allocation, including regular users, lenders, and the protocol’s economic model. The flaw was discovered during a formal audit when a test case demonstrated that a single lock could be used to increase a gauge’s relative weight from the expected 50 % to over 95 % by performing twenty delegations. The problem is subtle because the gauge weight appears to grow smoothly and there is no explicit counter that limits the number of votes per lock, making the inflation easy to miss in routine monitoring. Conceptually, the bug belongs to the class of vote‑replay or vote‑inflation attacks caused by using mutable state (current block) to compute voting power instead of an immutable snapshot. To remediate, the protocol should compute voting power from a block that is a fixed distance in the past, enforce a one‑vote‑per‑lock‑per‑period rule, and optionally define a governance‑controlled voting window during which votes are accepted. This prevents an attacker from repeatedly delegating and voting within the same period, thereby preserving the intended accounting relationship between locked tokens and gauge weight and protecting the fairness of reward distribution.

## Proof of Concept
`VotingEscrow` has a delegate mechanism which lets a user delegate the voting power to another user. The `GaugeController` allows voters who locked native in `VotingEscrow` to vote on the weight of a specific gauge.

Due to the fact that users can delegate their voting power in the `VotingEscrow`, they may vote once in a gauge by calling `vote_for_gauge_weights()`, delegate their votes to another address and then call again `vote_for_gauge_weights()` using this other address.

A POC was built in Foundry, add the following test to `GaugeController.t.sol`:

```solidity
function testDelegateSystemMultipleVoting() public {
    vm.deal(user1, 100 ether);
    vm.startPrank(gov);
    gc.add_gauge(user1);
    gc.change_gauge_weight(user1, 100);
    vm.stopPrank();

    vm.deal(user2, 100 ether);
    vm.startPrank(gov);
    gc.add_gauge(user2);
    gc.change_gauge_weight(user2, 100);
    vm.stopPrank();

    uint256 v = 10 ether;

    vm.startPrank(user1);
    ve.createLock{value: v}(v);
    gc.vote_for_gauge_weights(user1, 10_000);
    vm.stopPrank();

    vm.startPrank(user2);
    ve.createLock{value: v}(v);
    gc.vote_for_gauge_weights(user2, 10_000);
    vm.stopPrank();

    uint256 expectedWeight_ = gc.get_gauge_weight(user1);

    assertEq(gc.gauge_relative_weight(user1, 7 days), 50e16);

    uint256 numDelegatedTimes_ = 20;

    for (uint i_; i_ < numDelegatedTimes_; i_++) {
        address fakeUserI_ = vm.addr(i_ + 27); // random num
        vm.deal(fakeUserI_, 1);

        vm.prank(fakeUserI_);
        ve.createLock{value: 1}(1);

        vm.prank(user1);
        ve.delegate(fakeUserI_);

        vm.prank(fakeUserI_);
        gc.vote_for_gauge_weights(user1, 10_000);
    }

    // assert that the weight is approx numDelegatedTimes_ more than expected
    assertEq(gc.get_gauge_weight(user1), expectedWeight_*(numDelegatedTimes_ + 1) - numDelegatedTimes_*100);

    // relative weight has been increase by a lot, can be increased even more if wished
    assertEq(gc.gauge_relative_weight(user1, 7 days), 954545454545454545);
}
```

## Recommendation
The vulnerability comes from the fact that the voting power is fetched from the current timestamp, instead of n blocks in the past, allowing users to vote, delegate, vote again and so on. Thus, the voting power should be fetched from n blocks in the past.

Additionally, note that this alone is not enough, because when the current block reaches n blocks in the future, the votes can be replayed again by having delegated to another user n blocks in the past. The exploit in this scenario would become more difficult, but still possible, such as: vote, delegate, wait n blocks, vote and so on. For this reason, a predefined window by the governance could be scheduled, in which users can vote on the weights of a gauge, n blocks in the past from the scheduled window start.

Chosen as best due to the clear and concise explanation, including business impact on the protocol, and including an executable PoC.
