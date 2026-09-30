# [M] Loss of Staked Funds With Wrongly Triggered tier2Farm::kill()

## Summary
Severity: Medium
Contest weight: 0.4042
Dataset id: 12775
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Plexus, most contracts have been equipped with a built-in kill() functionality that allows the owner to explicitly self-destruct the specific contract. However, this capability needs to exercise extra care as these contracts may directly interact with external DeFi protocol. Because of that, these contracts may effectively act as the holders of staked funds in these external DeFi protocols. To elaborate, we show below the kill() routine from the tier2Farm contract. A blind call of it makes it unable to further unstake the funds, if any, from the external DeFi protocols.
```solidity
function kill() virtual public onlyOwner {
    selfdestruct(owner);
}
```
A better approach may be to verify there are no assets remaining in current contract and only invoke selfdestruct() (line 289) after the successful validation. Note all current tier2 contracts, e.g., tier2Aave, tier2Farm, tier2Pickle, and tier2Aggregator, share the same issue.

## Recommendation
Revise the kill() logic to ensure staked funds are not at risk.
