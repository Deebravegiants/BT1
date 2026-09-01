# [H] Insufficient Transfer Cooldown Period in CrossChainProofOfHumanity Contract

## Summary
Severity: High
Chain: Smart contract
Component: Proof-Of-Humanity-V2
Published: 2024-08-31
Source: https://github.com/hats-finance/Proof-Of-Humanity-V2-0xef0709445d394a22704850c772a28a863bb780b0/issues/130
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x862ae3b46424778adce4576dea5bd977d1255d51e550312e4f169ab25f75050f
**Severity:** high

**Description:**
**Description**\
The `CrossChainProofOfHumanity` contract implements a cooldown period to prevent abuse of the cross-chain humanity transfer feature.

However, the current cooldown period is set to just 7 seconds, which is extremely short for cross-chain operations. 

This brief cooldown fails to provide adequate protection against rapid transfers and potential exploitation of the system.

The short cooldown period undermines the security measures intended to prevent abuse, such as evading revocation attempts or causing inconsistencies across different chains. 

It also doesn't allow sufficient time for transaction finality on most blockchain networks, potentially leading to race conditions and state inconsistencies.

**Attack Scenario**\
An attacker could exploit this short cooldown period in several ways:

Rapid Chain-Hopping: The attacker could transfer their humanity claim across multiple chains in quick succession, potentially evading revocation attempts or confusing monitoring systems.

Denial of Service: By repeatedly transferring humanity claims, an attacker could overwhelm the bridge systems and associated contracts with a high volume of transfer requests.

Circumvention of Governance: The short cooldown doesn't allow enough time for governance mechanisms to intervene in case of suspicious activity, rendering such safeguards ineffective.

**Recommendation**
Increase the cooldown period to maybe 1 day (86400)
