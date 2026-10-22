# [M] Centralization issues

## Summary
Severity: Medium
Contest weight: 0.0810
Dataset id: 3956
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Hybrid NFT protocol uses OpenZeppelin AccessManager to guard sensitive calls withing the contracts. These include: Token::mint, Token::setTrusted, NFT::mint, NFT::burn, Referral::generateReferrerId, Bridge::closeMint, Bridge::enableBridge, Bridge::pullGenesisShare. Were the admin account in control of AccessManager to be compromised all the above calls would be available to an attacker which would cause great harm to the project.

## Recommendation
We recommend the protocol to use at least a multisig for the admin control over AccessManager or a DAO setup. Also consider having a timelock setup so that users can react to changes done to the protocol. Blerb:
