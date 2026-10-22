# [M] `RewardThrottle._sendToDistributor

## Summary
Severity: Medium
Contest weight: 0.6087
Dataset id: 18141
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the reward distribution routine of the RewardThrottle contract. The internal function _sendToDistributor iterates over a list of distributors, calculates each distributor's share of the total reward amount, and then transfers the calculated share to the distributor before invoking the distributor's declareReward function. The LinearDistributor implementation of declareReward is protected by an onlyActive modifier that reverts the call when the distributor is marked inactive. Because _sendToDistributor does not check the active status of each distributor before making the external call, the presence of a single inactive distributor causes the entire loop to revert, aborting all pending transfers. This flaw occurs whenever the function is called with a non‑zero reward amount and the allocation array contains at least one inactive distributor, which can happen after a governance action, a contract upgrade, or any condition that deactivates a distributor. The root cause is the lack of defensive programming around external calls that may fail independently; the contract assumes all distributors are always active and treats a revert from one as acceptable, which is not true. An attacker or any party with the ability to deactivate a distributor can therefore trigger a denial‑of‑service condition, preventing rewards from being distributed to all legitimate recipients. From a user perspective the symptoms are that expected reward balances remain zero, UI elements show no new rewards, and transactions that should credit users revert with a generic error, leading to confusion and loss of confidence. The issue belongs to the class of “partial‑failure denial‑of‑service” bugs where a batch operation does not tolerate a single failing external call. It is hard to notice because the function works correctly as long as all distributors stay active; the failure only appears when an inactive distributor is introduced, making the problem intermittent and not obvious from static analysis alone. The recommended remediation is to filter out inactive distributors before attempting a transfer, or to wrap each declareReward call in a try/catch block and continue with the remaining active distributors, or to redesign the distributor interface so that reward declaration does not revert for inactive contracts. By ensuring that only active distributors are processed, the protocol can maintain its accounting guarantees, prevent reward loss, and uphold the expected business logic that users receive their allocated rewards regardless of the state of unrelated distributors.

## Proof of Concept
`RewardThrottle._sendToDistributor()` distributes the rewards to several distributors according to their allocation ratios.

```solidity
File: 2023-02-malt\contracts\RewardSystem\RewardThrottle.sol
575:   function _sendToDistributor(uint256 amount, uint256 epoch) internal {
576:     if (amount == 0) {
577:       return;
578:     }
579: 
580:     (
581:       uint256[] memory poolIds,
582:       uint256[] memory allocations,
583:       address[] memory distributors
584:     ) = bonding.poolAllocations();
585: 
586:     uint256 length = poolIds.length;
587:     uint256 balance = collateralToken.balanceOf(address(this));
588:     uint256 rewarded;
589: 
590:     for (uint256 i; i < length; ++i) {
591:       uint256 share = (amount * allocations[i]) / 1e18;
592: 
593:       if (share == 0) {
594:         continue;
595:       }
596: 
597:       if (share > balance) {
598:         share = balance;
599:       }
600: 
601:       collateralToken.safeTransfer(distributors[i], share);
602:       IDistributor(distributors[i]).declareReward(share); // @audit will revert if one distributor is inactive
```

And `LinearDistributor.declareReward()` has an `onlyActive` modifier and it will revert in case of `inactive`.

```solidity
File: 2023-02-malt\contracts\RewardSystem\LinearDistributor.sol
098:   function declareReward(uint256 amount)
099:     external
100:     onlyRoleMalt(REWARDER_ROLE, "Only rewarder role")
101:     onlyActive
102:   {
```

As a result, `RewardThrottle._sendToDistributor()` will revert if one distributor is inactive rather than working with active distributors only.

## Recommendation
I think it’s logical to continue to work with active distributors in `_sendToDistributor()`.
