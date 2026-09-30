# [M] `_syncVotingPower` can revert in underflow in `NFTBoostVault.sol` and `ARCDVestingVault.sol`

## Summary
Severity: Medium
Contest weight: 0.3342
Dataset id: 18901
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an arithmetic underflow that can occur in the internal function responsible for synchronising a delegatee's voting power when the voting power of a user is reduced. The function calculates the change in voting power as a signed integer, and when the change is negative it attempts to subtract the absolute value of the change from the delegatee's current voting power using the expression delegateeVotes - uint256(change * -1). Because there is no check that delegateeVotes is at least as large as the amount being subtracted, a situation where the reduction exceeds the delegatee's existing voting power triggers a uint256 underflow, causing the transaction to revert. This bug appears in two vault contracts that manage boosted voting power for NFTs and vesting grants. It manifests when an NFT with a high multiplier is withdrawn or when an admin revokes a grant, both of which can cause a large negative change. From a user's perspective the symptom is a transaction that fails with an "execution reverted" error at the moment they expect a withdrawal, a grant revocation, or a voting power update; the user sees no funds returned and the expected vote count does not change. The root cause is the unchecked subtraction of a potentially larger value than the current balance, a classic example of an integer underflow bug in smart contracts. The issue was discovered during a manual audit that examined the voting‑power synchronisation logic and identified the unsafe cast from a signed to an unsigned integer without a safety guard. It can be hard to notice because the underflow only occurs in edge cases where the reduction is larger than the current delegated votes, which may not be exercised in normal test scenarios. Exploitation does not require sophisticated tooling; any user who holds a boosted NFT or a vesting grant can trigger the underflow by withdrawing the asset or by an admin revoking the grant, causing the transaction to revert and effectively denying service to the affected account. The impact is a denial‑of‑service condition: users cannot withdraw their NFTs or have their grants revoked, and the protocol's voting tally may become inconsistent because the update never happens. The bug violates the protocol’s accounting assumptions that voting power can only be decreased down to zero, not below. A proper fix is to ensure that before performing the subtraction the contract verifies that delegateeVotes is greater than or equal to the absolute change, and if not, to set the new voting power to zero or use a saturating subtraction that prevents underflow. This change restores the intended business logic that voting power can be reduced but never become negative, eliminating the revert and allowing normal withdrawals and revocations.

## Proof of Concept
Note this function:
    
function _syncVotingPower(address who, NFTBoostVaultStorage.Registration storage registration) internal {
    History.HistoricalBalances memory votingPower = _votingPower();
    uint256 delegateeVotes = votingPower.loadTop(registration.delegatee);

    uint256 newVotingPower = _currentVotingPower(registration);
    // get the change in voting power. Negative if the voting power is reduced

    int256 change = int256(newVotingPower) - int256(uint256(registration.latestVotingPower));

    // do nothing if there is no change
    if (change == 0) return;
    if (change > 0) {
        votingPower.push(registration.delegatee, delegateeVotes + uint256(change));
    } else {
        // if the change is negative, we multiply by -1 to avoid underflow when casting
        votingPower.push(registration.delegatee, delegateeVotes - uint256(change * -1));
    }

    registration.latestVotingPower = uint128(newVotingPower);

    emit VoteChange(who, registration.delegatee, change);
}

We need to pay special attention to this line of code:
    
votingPower.push(registration.delegatee, delegateeVotes - uint256(change * -1));

It is possible that `delegateeVotes` - changes can revert in underflow. This only happens when we try to reduce the voting power.

In `_withdrawNFT`, if an NFT with a high multipler is removed in `NFTBoostVault.sol` it can cause the [voting power to decrease](https://github.com/code-423n4/2023-07-arcade/blob/f8ac4e7c4fdea559b73d9dd5606f618d4e6c73cd/contracts/NFTBoostVault.sol#L569).
    
// update the delegatee's voting power based on multiplier removal
_syncVotingPower(msg.sender, registration);

Or, in `ARCDVestingVault.sol` when an admin tries to [revoke a user’s grant](https://github.com/code-423n4/2023-07-arcade/blob/f8ac4e7c4fdea559b73d9dd5606f618d4e6c73cd/contracts/ARCDVestingVault.sol#L175).
    
// update the grant's withdrawn amount
if (amount == withdrawable) {
    grant.withdrawn += uint128(withdrawable);
} else {
    grant.withdrawn += uint128(amount);
    withdrawable = amount;
}

// update the user's voting power
_syncVotingPower(msg.sender, grant);

## Recommendation
Before calling `delegateeVotes - uint256(change * -1)`, make sure `delegateeVotes > uint256(change * -1)`, otherwise just set to 0.

Will look into underflow scenarios here where there is a multiplier boost.
