# [H] Stale price can be disputed but still accepted

## Summary
Severity: High
Contest weight: 0.2957
Dataset id: 17647
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The shift() function has no validation that stops a proposer from creating a new proposal with valid but outdated price data.  
Oct 3rd to Oct 5th.  
If an attacker submitted a proposal with the price from a long time ago, say 10 days, this proposal can and will be disputed.  
However, dispute()->validate() won't refetch the new price data as long as nonceIsValid (L183-198), so that the price from 10 days ago will be passed to _settleDispute() as the validValue (OptimisticChainlinkOracle.sol#L191, OptimisticOracle.sol#L188,207).  
Even though the dispute() won't push the stale price to the Collybus immediately, instead, it creates a new proposal in the name of the OptimisticChainlinkOracle contract itself as the proposer. But since this proposal is not bonded, it may not get disputed, so the stale price can likely be shifted to the collybus soon after the dispute.

## Recommendation
Considering the fact that the nonce is computed on-chain in shift() (L156). It can and should make sure the new proposal is within the proposeWindow.  
Thus, we can get rid of the proposeWindow check in the validate() function.  
in shift. The proposeWindow was removed in favor of checking that the proposed value is newer than the previous proposal. This is preferred because it gives us a generic way of handling different token types with different update rates. The side-effect is that now price updates can start to lag behind if for example the dispute window is let's say 6 hours and the chainlink feed is updated every hour, then a possible attack vector would be to push the next computed(compared to the current proposed value) round instead of the latest or a newer one and in time this can lead to stale prices being pushed or that an attacker has a big pool of chainlink rounds to choose from. In order to avoid this problem we will have a keeper running that ensures the price updates do not fall behind. If we detect any lag the keeper will execute a ‘push() which will update to the latest chainlink value().  
The reason we do not check the round timestamp in shift is that it makes the optimistic proposal system obsolete by making shifts more expensive that pushes.
