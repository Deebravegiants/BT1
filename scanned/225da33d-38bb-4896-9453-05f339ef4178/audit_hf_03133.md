# [M] Malicious proposers can frontrundispute() and

## Summary
Severity: Medium
Contest weight: 0.4386
Dataset id: 17618
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
dispute() is a permissionless function that anyone can call to claim all the bonds from an invalid proposal. This allows the malicious proposers to claw back their bond by front-running dispute() and minimizing the penalty.  
When a malicious proposal front run dispute() on their own invalid proposal, the real cost is the gas cost of the dispute transaction.  
A very sophisticated attacker can deliberately create a few invalid proposals, frontrun others' dispute() transactions, and waste their gas.  
As a result, the other dispute bots will be pushed out as they often get front run, resulting in those bots wasting gas costs on failed transactions.  
After a while, the attacker can casually add an invalid proposal, and there is a chance that no other bots will dispute(), and even if they do, the attacker will just frontrun them again, with very minimal cost.  
Even if the bondSize is very large, say $5000, it becomes insufficient to prevent malicious proposals. As the front run cost can be as low as $50, and the potential gains with a malicious price proposal can be >$500k.

## Recommendation
1. Instead of sending all the bondSize to the receiver of dispute(), consider sending only a portion of the bond, say 50%, and use the other 50% as rewards for the honest proposers; then the real cost for a malicious proposer would be at least 50% of the bondSize.  
2. Consider optimizing the gas cost for dispute() a proposal that is already been disputed, the current implementation is quite expensive.  
Specifically, consider moving L345-L350 to before L301, so that it reverts earlier and saves gas for the bots:  
https://github.com/fiatdao/delphi-v2/blob/96570ef83f978616ef4a4a6057f69364a1206c57/src/OptimisticOracle.sol#L345-L350  
```solidity
if (proposals[rateId] != computeProposalId(rateId, proposer, value, uint256(nonce))) {
    revert OptimisticOracle__settleDispute_unknownProposal();
}
```
We are going to restrict the bond method and revoke rights to call bond from slashed proposers. The only attack vector that remains is a 1 hour long block withholding attack. Though this is only solvable by having more complex range bound checks in Collybus. Which we might look into in the future. I'll leave the bondSize payout as is.  
An attacker can attempt to use another address to bond, but it would have to be whitelisted in order to do so.
