# [H] vePeg#delegate lacks any access control allowing all votes to be stolen through delegation

## Summary
Severity: High
Contest weight: 0.5339
Dataset id: 2738
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function delegate(uint256 _from, uint256 _to) public {
    return _delegate(_from, _to);
}
```

We see above that when delegating there is no access control. This means that anyone can call this function and re-delegate for anyone else. This allows a malicious user to steal all voting power. They could use this to funnel rewards towards a beneficial pool or use it to vote on governance actions.

## Recommendation
delegate should check that msg.sender is approved by the owner of from.
