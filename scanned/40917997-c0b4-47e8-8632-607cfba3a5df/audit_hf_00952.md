# [H] Attacker can remove voting power from more than 52 minutes ago due to maximum queue length

## Summary
Severity: High
Contest weight: 0.9072
Dataset id: 3007
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The voting power queue of each user has a maximum length of MAX_HISTORY_LENGTH. In the current implementation, the queue can have a maximum length of 256:
```solidity
// Max length of any voting history. Prevents gas exhaustion
// attacks from having too-large history.
uint256 public constant MAX_HISTORY_LENGTH = 256;
```
For example, when pushing a new checkpoint into the voting power queue in changeDelegation(), MAX_HISTORY_LENGTH is passed to push():
```solidity
// Store the increase in power
votingPower.push(newDelegate, newDelegateVotes + userBalance, MAX_HISTORY_LENGTH);
```
In BoundedHistory.push(), a new checkpoint with the current block number is added to the front of the queue. Afterwards, if the queue's new length exceeds 256, the oldest checkpoint is deleted from the back of the queue:
```solidity
} else if (length - minIndex >= maxLength) {
    // We need to push to the array, but if array is full to maxLength, so
    // we clear the oldest entry and increment the minIndex
    _clear(minIndex, ++minIndex, storageData);
}
```
However, such an implementation allows an attacker to force a user's history to only store the last MAX_HISTORY_LENGTH blocks. Since the maximum queue length is 256 in the current implementation, an attacker can force the contract to only store a user's voting power history for the last 256 blocks. This can be achieved by:
- At every block, call changeDelegation() with newDelegate set to the victim's address. This will push a new entry into votingPower for the current block number.
- Due to the 256-entry limit for votingPower, after changeDelegation() is called enough times for votingPower to hold more than 256 entries, push() will start to delete the oldest entry.
- After 256 blocks, all past entries in votingPower will have been deleted, so the oldest entry will be from 256 blocks ago.
If queryVotePower() is called to query a user's voting power more than 256 blocks ago, the function will revert as there is no record of the user's voting power before or during blockNumber.
Since mainnet produces a block every 12 seconds, 256 blocks corresponds to 51.2 minutes, which means an attacker can forcefully remove a victim's voting power history from more than ~52 minutes ago.
Note that deposit() and withdraw() can also be used to perform the same attack, since they also add checkpoints to the delegate's queue with _addVotingPower() and _subtractVotingPower().

## Recommendation
Consider removing the MAX_HISTORY_LENGTH limit on the checkpoint queue (i.e. the queue can be infinitely long). This can be achieved by setting MAX_HISTORY_LENGTH to an extremely large value, such as type(uint256).max, or reverting the contract to use History instead of BoundedHistory.
To prevent the issue of queryVotePower() running out of gas when the queue is too long, avoid clearing stale blocks in the queue when queryVotePower() is called:
```solidity
function queryVotePower(
    address user,
    uint256 blockNumber,
    bytes calldata
) external override returns (uint256) {
    // Get our reference to historical data
    BoundedHistory.HistoricalBalances memory votingPower = _votingPower();
    // Find the historical data and clear everything more than 'staleBlockLag' into the past
    return
        votingPower.findAndClear(
            user,
            blockNumber,
            block.number - STALE_BLOCK_LAG
        );
    return this.queryVotePowerView(user, blockNumber);
}
```
This would be similar to other implementations of voting checkpoint queues, such as OpenZeppelin's Votes.sol, which only adds checkpoints to the queue and but never removes them.
The only functions remaining that iterate through the checkpoint queue would be queryVotePower() and queryVotePowerView(), which performs a maximum of log(n) iterations using binary search.
Therefore, there isn't a need to remove stale checkpoints from the queue as there is no risk of any function ever running out-of-gas, resulting in DOS.
