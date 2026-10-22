# [M] Absence of Minimum delayBlocks

## Summary
Severity: Medium
Contest weight: 0.3819
Dataset id: 6831
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Owner can accidentally set delayBlocks as 0 (or a very small delay block) which will collapse the whole fraud protection mechanism. Since there is no check for minimum delay before setting a new delay value so even a low value will be accepted by setDelayBlocks function

```solidity
function setDelayBlocks(uint256 _delayBlocks) public onlyOwner {
    require(_delayBlocks != delayBlocks, "!delayBlocks");
    emit DelayBlocksUpdated(_delayBlocks, delayBlocks);
    delayBlocks = _delayBlocks;
}
```

## Recommendation
Introduce a variable minDelay which tells the minimum possible delay allowed by the contract.
Any attempt to change delay value using setDelayBlocks function should ensure that new delay is larger/equal to minDelay
