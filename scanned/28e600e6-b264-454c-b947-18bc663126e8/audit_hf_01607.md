# [M] M-01 | Attestor Lacks Payable Function

## Summary
Severity: Medium
Contest weight: 0.1736
Dataset id: 8640
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Ethereum Attestation Service (EAS) allows users to make attestations and send ETH if the resolver is expected to be payable. If the amount of ETH sent exceeds the value set in the attestation, EAS refunds the remaining amount to the sender, as shown in the EAS contract code. To support cases where the remaining amount is refunded to the Cyfrin Attester, Cyfrin added a withdrawEth method that allows the admin to withdraw accumulated ETH. However, the current Cyfrin Attester contract does not include a receive() payable function or a fallback function to accept ETH. As a result, if a refund is attempted, the transaction would revert. While the current resolver used by Cyfrin (Certifications) is not payable, Cyfrin may support different schemas with various resolvers in the future. In such cases, the attester might receive ETH refunds if Cyfrin deploys a payable resolver for those future schemas and attestations. If we understand correctly, this is the reason Cyfrin included the withdrawEth function in the attester. If this issue goes unfixed, then for payable resolvers, Cyfrin would need to deploy a new attester with the ability to receive ETH, creating multiple on-chain identities for Cyfrin—which is not desirable.

## Recommendation
Consider adding a receive() payable function or a fallback function to the Cyfrin attestor to handle incoming ETH properly.
