# [H] H-08 | bAsset Shorts Can Make A Guaranteed Profit

## Summary
Severity: High
Contest weight: 0.2706
Dataset id: 21461
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Baseline V2 system it is possible for a user to arbitrage the system in order to make guaranteed profit on a short.
This arbitrage can occur with the following actions:
1. Bob borrows X bAssets from Alice
2. Bob buys Y bAssets to move the anchor up after sweeping
3. Bob sells Y bAssets and achieves a lower pool price than before his buy because:
   - The anchor has moved up, meaning there is less capacity for the same amount of liquidity (though in many cases this is offset by discovery surplus)
   - On his buy he was buying in the discovery (higher liquidity) and on his sell he was selling in the anchor (lower liquidity)
4. Slide moves the discovery liquidity back down so that Bob is able to buy the bAssets back at a lower average price, due to higher liquidity at a lower price.
5. Bob can pay back the bAssets he borrowed from Alice while the bAsset price is lower than when he borrowed, representing a profitable short.
Bob has made a guaranteed profit of the delta on this short.

## Proof of Concept
https://github.com/GuardianAudits/baseline-team-1-pocs/blob/POC_ARB_ATTACK_FULL/test/guardian/pocs/arbAttack.t.sol

## Recommendation
Consider restructuring the way liquidity is managed in the Baseline system, such that there are no immediate large liquidity shifts which can be arbitraged in this way.
