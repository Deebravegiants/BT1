# [C] C-08 | aspTKNOracle Can Be Manipulated With Donation

## Summary
Severity: Critical
Contest weight: 0.2493
Dataset id: 22180
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In a previous audit, it was reported that the aspTKN oracle could be manipulated through a donation of spTKN (see https://hackmd.io/@tapir/SyxqzohUA#H-9-aspTKN-oracle-can-be-manipulated). While this has been fixed through the accounting of assets with a storage variable, this attack is still possible through donation of reward tokens which then gets compounded into spTKNs (assets). _processRewardsToPodLp is called on every external user action, which checks for balanceOf reward tokens in the contract, and then converts the reward tokens to spTKNs. Similar to the previously reported issue, although the attacker loses the donated tokens, they can manipulate the oracle pricing to borrow more tokens from the lending protocol, exploiting the system. Low liquidity pods are more susceptible to such attacks.

## Proof of Concept
https://github.com/GuardianAudits/peapods-1/pull/12/files#diff-237b2eff3889a3d31966682e9e41818e0e2c1cbd65930d57f87f842a75c6a7ea

## Recommendation
No straightforward solution as existing reward flow relies on transferring tokens to the AutoCompounder. Consider re-designing the reward and compounding flow to ensure the oracle pricing cannot be easily manipulated through a donation of reward tokens.
