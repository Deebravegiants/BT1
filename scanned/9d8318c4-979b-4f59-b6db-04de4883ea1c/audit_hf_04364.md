# [H] H-02 | Claim Rewards Callback Message Not Executable

## Summary
Severity: High
Contest weight: 0.1894
Dataset id: 21569
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can claim ORDER and esORDER rewards based on the merkle distributions. The issue arises when claiming esORDER, as the amount claimed will be staked, but will also try to send a ClaimRewardBackward payload to the Vault chain. The internal vaultRecvFromLedger in ProxyLedger contract will fail as this callback performs the following check: require(message.token == LedgerToken.ORDER && message.tokenAmount > 0, "InvalidClaimRewardBackward"); Therefore, every esORDER claim request will block the LayerZero pathway for the destination chain, as no new messages can be executed before clearing the failed one.

## Proof of Concept
https://github.com/GuardianAudits/omnichain-ledger-1/pull/1/files

## Recommendation
Avoid sending the message back to Vault Chain when claiming esORDER rewards, by early returning after _stake or creating an else statement.
