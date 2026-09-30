# [M] Multisig Security Enhancements

## Summary
Severity: Medium
Contest weight: 0.0983
Dataset id: 15953
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Current multisig setup uses 3/5 threshold (60%) with all internal signers. While functional, this configuration could be strengthened with a goal of 70% for medium and high risk operations.
For further discussion, see this article, The Right Way To Multisig.

## Recommendation
1. Increase security through external signers:
• Short-term: Add trusted third party (e.g., security provider partner) as 6th signer.
• Adjust threshold to 4/6 (66.7%) as an immediate improvement.
• Long-term: Consider expanding to 5/7 configuration as team and protocol grow.
• Document verification responsibilities for external signer.
2. Implement formal key management procedures:
• Annual review of signer set composition.
• Documented procedures for signer replacement.
• Regular testing of recovery scenarios.
• Clear criteria for emergency key revocation.
3. Enhance signing procedures:
• Require out-of-band transaction hash verification.
• Implement mandatory cool-down period for large transfers (Note: This is currently not readily available for Aptos multisig wallets but something to keep in mind for the future).
• Create transaction templates for common operations.
• Document specific verification steps for each transaction type.
