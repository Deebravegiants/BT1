# [C] CRT-1 Impossible withdraw for smart contract

## Summary
Severity: Critical
Contest weight: 0.0553
Dataset id: 9268
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability originates from the way StakingRewardsV3 handles NFT deposits. The contract accepts NFTs via the ERC721 safeTransferFrom function, which triggers a callback to the recipient contract's onERC721Received method. If the depositing contract does not implement this callback, the safe transfer succeeds only because the staking contract does not enforce the interface, but later when the user attempts to call withdraw the internal logic expects the token to have been received through the safe transfer flow. Because the onERC721Received hook is missing, the withdraw function encounters a revert condition and the NFT becomes permanently locked in the staking contract. This situation can be reproduced whenever a smart contract that lacks the ERC721Receiver interface deposits an NFT into StakingRewardsV3. From the user’s perspective the deposit transaction may appear to have succeeded – the UI shows a confirmation and an event is emitted – yet when the user later tries to retrieve the NFT, the transaction fails with a generic revert, leaving the balance displayed as zero or unchanged. The impact is severe: the staked NFT cannot be reclaimed, effectively removing the asset from the user’s control, which justifies the critical severity rating. The issue was identified during a formal security audit performed by MixBytes, which noted that the contract’s reliance on safeTransferFrom without a corresponding onERC721Received implementation creates an implicit requirement that is not documented for callers. The bug is subtle because the failure only manifests on withdrawal, not at deposit time, making it easy to miss during functional testing. To remediate the problem the staking contract should either enforce that callers implement ERC721Receiver, or, as recommended, replace the safeTransferFrom call with a plain transferFrom call that does not require a callback. This change removes the hidden dependency on onERC721Received and ensures that any contract, regardless of its interface, can safely deposit and later withdraw NFTs without risking a permanent lock.

## Recommendation
We recommend to use transferFrom() instead of safeTransferFrom().
