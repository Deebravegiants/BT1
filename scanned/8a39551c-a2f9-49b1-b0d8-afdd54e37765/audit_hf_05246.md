# [H] Unbounded depositAddresses can cause CompliantDepositRegistry::challengeLatestBatch to revert due to out of gas

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23426
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
CompliantDepositRegistry::challengeLatestBatch contains an unbounded loop that removes deposit addresses from the latest batch by calling `depositAddresses.pop()` repeatedly. When a large batch of deposit addresses is added via `CompliantDepositRegistry::addDepositAddresses`, challenging this batch could consume excessive gas, potentially exceeding the block gas limit and causing the transaction to revert. This creates a Denial of Service (DoS) vulnerability where legitimate challenges cannot be executed.

```solidity
function challengeLatestBatch() public onlyRole(CANCELER_ROLE) {
    require(latestBatchUnlockTime >= block.timestamp, NoChallengeAfterUnlock());
    uint256 _finalizedAddressesLength = finalizedAddressesLength;
    // Get rid of the challenged batch by removing it from the list
    uint256 batchLength = depositAddresses.length - _finalizedAddressesLength;
    for (uint256 i; i < batchLength; i++) {
        depositAddresses.pop();
    }<---------
    // Reset the challenge period to allow a new batch to be generated
    latestBatchUnlockTime = block.timestamp;
    emit BatchChallenged(_finalizedAddressesLength, block.timestamp, batchLength);
}
```

Impact: Large batches become unchallengeable, allowing malicious or incorrect deposit addresses to be finalized.

## Recommendation
Implement limits on the amount of addresses that can be added through `CompliantDepositRegistry::addDepositAddresses`.
