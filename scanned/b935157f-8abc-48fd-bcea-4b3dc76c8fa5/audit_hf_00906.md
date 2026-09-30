# [M] Signatures missing some parameters being signed

## Summary
Severity: Medium
Contest weight: 0.2603
Dataset id: 2670
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
createAgentWithSigWithNFT() for example signs projectId, base64RecParam, serverURL. However, it does not sign privateWorkerAddress or tokenId. This is an issue because although Base has a private mempool, the protocol integrates with Biconomy, which leverages ERC4337 and has a mempool for bundlers. Hence, the signatures will be available in the mempool and anyone can fetch them and submit it directly to base with other malicious tokenId or privateWorkerAddress.
Thus, users can be forced to create agents with token ids they didn't intend to use or use invalid worker addresses, DoSing them. Workers have incentive to do this as they can censor other workers this way from using other workers and only they will be able to make the deployments, censoring other workers. The protocol intends to benefit workers from their work, so they have incentive to do so.
crestal-network/blob/main/crestal-omni-contracts/src/BlueprintCore.sol#L491), the token address used can be another one that has a bigger cost and users end up paying more.
In createAgentWithSigWithNFT() and similar, tokenAddress, tokenId, privateWorkerAddress are not signed.
Internal Pre-conditions
None.
External Pre-conditions
None.
Attack Path
1. User sends signature to be used on createAgentWithSigWithNFT() or createAgentWithTokenWithSig() to the offchain protocol, which forwards it to Biconomy, adding the user operation to the mempool.
2. Attacker picks up the signature from the eip4337 mempool and submits the onchain transaction with other malicious inputs.
Worker censors other workers, DoSes users, makes them pay fees without getting services and ultimately forces users to use the attacker worker's services, who gets illegitimate fees. Or, attacker steals tokens from users by specifying a different token address. Or, another token id ownership is used.

## Proof of Concept
Here is how the biconomy bundler works (which is the same as the typical bundler):
Aggregating userOps in an alternative mempool to normal Ethereum Transactions
Attacker can become a bundler and listen to the same mempool and perform the attack.

## Recommendation
Sign all parameters.
