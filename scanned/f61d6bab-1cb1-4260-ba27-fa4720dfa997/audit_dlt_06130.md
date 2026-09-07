# [M] User assets will be affected, if EthGenesisVault, if isn't Collateralized

## Summary
Severity: Medium
Chain: Smart contract
Component: StakeWise
Published: 2023-08-27
Source: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/118
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Submission hash (on-chain):** 0x5bf89400ff29ef77025bade7f19cc3022b7c6a28aa4a0f72646d2310d2c9720b
**Severity:** medium

**Description:**
**Description**\
In vaults, if a user deposits ETH to the vault and doesn't register the validator updateState doesn't affect the user's asset but in EthGenesisVault As the Genesis Vault is linked to the legacy Stakewise V2 system, the updateState function affects the user's asset.
[https://github.com/stakewise/v3-core/blob/c82fc57d013a19967576f683c5e41900cbdd0e67/contracts/vaults/ethereum/EthGenesisVault.sol#L107-L137](https://github.com/stakewise/v3-core/blob/c82fc57d013a19967576f683c5e41900cbdd0e67/contracts/vaults/ethereum/EthGenesisVault.sol#L107-L137)
 So if a user deposits ETH to the vault and doesn't register the validator, As the Genesis Vault is linked to the legacy Stakewise V2 system if anyone calls updatesate, it affects the user's asset. 



**Impact **\

- affects the user's assets.

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
As "The Genesis vault will become available for the users(v2 users) (added to UI) only after first harvest or validator
registration happens.", if the vault isn't Collateralized, there is no need for updatestate.
