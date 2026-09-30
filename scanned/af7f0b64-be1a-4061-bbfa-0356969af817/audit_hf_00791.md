# [H] H-12 | Max LTV Can Be Abused On Small Price Changes

## Summary
Severity: High
Contest weight: 0.2623
Dataset id: 2527
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The given maxLtv value provided by the protocol as a deployment parameter is 1e18 which equals a 1:1 ratio LTV. This means users can borrow assets for $100 by providing $100 collateral if the LTV for the given collateral token is set to 1e18. Therefore only a small price change not updated in the oracle because of deviation, or not yet updated as the attacker front runs the oracle update can be abused to make risk-free profit and put the pool into bad debt.
Here is a possible attack scenario:
• The pool owner adds a new asset to the BasePool with a 1e18 LTV (1:1 ratio)
• The price of this asset is currently outdated as chainlinks deviation threshold is not reached (for example 0.5% deviation and 0.4% change)
• The attacker takes a flash loan of the given asset and borrow all funds with it
• The attacker sells the funds from the BasePool for a 0.4% - trading fees profit and pays back the flashloan
• The attacker made a large profit depending on the size of the pool and the pool will be in bad debt as soon as the oracle price is updated

## Proof of Concept
https://github.com/GuardianAudits/sentiment-team-1/compare/POC_ONE_TO_ONE_RATIO_LTV?expand=1

## Recommendation
Use a lower maxLtv value.
