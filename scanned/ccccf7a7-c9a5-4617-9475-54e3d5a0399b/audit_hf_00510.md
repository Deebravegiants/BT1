# [M] M-02 | Inaccessible onlyOwner Functions

## Summary
Severity: Medium
Contest weight: 0.0808
Dataset id: 1968
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Since the Vault contract will be executing the onlyOwner createEpoch() function, it will be set as the owner of the foil system. The ConfigurationModule.updateMarket() function can be called by the Foil owner to update the market parameters. However, this function is never called in the Vault contract. This means the market can never be updated once the ownership is transferred to the contract. There is also no call to transferOwnership in Vault, so you can't just use a new vault as the owner.

## Recommendation
Add calls to updateMarket and transferOwnership in the vault.
