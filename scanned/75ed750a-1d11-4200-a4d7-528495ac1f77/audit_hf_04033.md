# [H] QVSimpleStrategy never updates

## Summary
Severity: High
Contest weight: 0.8774
Dataset id: 20461
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
QVSimpleStrategy._allocate calls _hasVoiceCreditsLeft to check that the recipient has voice credits left to allocate
https://github.com/allo-protocol/allo-v2/blob/main/allo-v2/contracts/strategies/qv-simple/QVSimpleStrategy.sol#L121
```solidity
function _allocate(bytes memory _data, address _sender) internal virtual override {
    // check that the recipient has voice credits left to allocate
    if (!_hasVoiceCreditsLeft(voiceCreditsToAllocate, allocator.voiceCredits)) revert INVALID();
    _qv_allocate(allocator, recipient, recipientId, voiceCreditsToAllocate, _sender);
}
```
QVSimpleStrategy._hasVoiceCreditsLeft checks _voiceCreditsToAllocate + _allocatedVoiceCredits <= maxVoiceCreditsPerAllocator
https://github.com/allo-protocol/allo-v2/blob/main/allo-v2/contracts/strategies/qv-simple/QVSimpleStrategy.sol#L144
```solidity
function _hasVoiceCreditsLeft(uint256 _voiceCreditsToAllocate, uint256 _allocatedVoiceCredits)
    internal
    view
    override
    returns (bool)
{
    return _voiceCreditsToAllocate + _allocatedVoiceCredits <= maxVoiceCreditsPerAllocator;
}
```
The problem is that allocator.voiceCredits is always zero. Both QVSimpleStrategy and QVBaseStrategy don't update allocator.voiceCredits. Thus, allocators can cast more votes than maxVoiceCreditsPerAllocator.
Every allocator has an unlimited number of votes.

## Recommendation
Updates allocator.voiceCredits in QVSimpleStrategy._allocate.
```solidity
function _allocate(bytes memory _data, address _sender) internal virtual override {
    ...
    // check that the recipient has voice credits left to allocate
    if (!_hasVoiceCreditsLeft(voiceCreditsToAllocate, allocator.voiceCredits)) revert INVALID();
    allocator.voiceCredits += voiceCreditsToAllocate;
    _qv_allocate(allocator, recipient, recipientId, voiceCreditsToAllocate, _sender);
}
```
