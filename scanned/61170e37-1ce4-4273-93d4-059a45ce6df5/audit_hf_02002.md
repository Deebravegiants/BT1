# [M] Limit possibilities of recoverERC20()

## Summary
Severity: Medium
Contest weight: 0.0981
Dataset id: 11315
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Function recoverERC20() in contract MultiMerkleDistributor.sol allows the retrieval of all ERC20 tokens from the MultiMerkleDistributor.sol whereas the comment indicates it is only meant to retrieve those tokens that have been sent by mistake. Allowing to retrieve all tokens also enables the retrieval of legitimate ones. This way rewards cannot be collected anymore. It could be seen as allowing a rug pull by the project and should be avoided.
In contrast, function recoverERC20() in contract QuestBoard.sol does prevent whitelisted tokens from being retrieved.

## Recommendation
Prevent the retrieval of legitimate tokens. Because it is not possible to enumerate questRewardToken[] to identify legitimate tokens, an extra data structure is needed. Also be aware of dual entry point tokens.
