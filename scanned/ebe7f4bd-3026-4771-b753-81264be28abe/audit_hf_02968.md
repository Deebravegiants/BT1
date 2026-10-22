# [M] M-6 Centralization risks

## Summary
Severity: Medium
Contest weight: 0.1924
Dataset id: 16462
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The issue has been identified within the HanjiLOB.sol#L55 and HanjiWatchDog.sol contracts.
The current design of the contract grants significant centralized control to the administrator and pauser roles.
The administrator has extensive powers, including the ability to upgrade the contract to any arbitrary address, pause or unpause the contract, and configure critical settings. The pauser role can also pause and unpause the contract. This concentration of control introduces centralization risks, as a single compromised or malicious administrator or pauser could disrupt or manipulate the contract, leading to potential security breaches or operational failures. Additionally, allowing the pauser role to unpause the contract could be risky if the contract is in an unstable state, as it could inadvertently enable harmful operations.
Moreover, the owner of the HanjiWatchDog contract can upgrade the contract's implementation. If the new implementation is flawed or if the HanjiWatchDog contract is compromised, the creation of new orders in the HanjiLOB contract may be blocked.
The issue is classified as medium severity due to the potential impact on the contract's security and operational integrity if these roles are exploited.

## Recommendation
We recommend using a multisig wallet for both the administrator and pauser roles. This would require multiple approvals for critical actions like upgrading the contract, pausing, or unpausing, thereby reducing the likelihood of malicious or erroneous actions. Additionally, we advise disabling the ability for the pauser role to unpause the contract, reserving this capability solely for the administrator role under the protection of a multisig wallet.
This would help ensure that the contract can only be resumed under secure and verified conditions.
