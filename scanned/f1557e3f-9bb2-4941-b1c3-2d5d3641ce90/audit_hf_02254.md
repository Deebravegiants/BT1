# [M] Business Logic Error in getOfferingTokens()

## Summary
Severity: Medium
Contest weight: 0.5904
Dataset id: 12391
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.1, the Legends Never Die users can stake their LND tokens into Legend vault and will get BNB-ETH plus BEP20 tokens as rewards. The BNB-ETH reward will come from the auction lobby contribution. When reviewing the implementation of the MasterVault contract, we notice that the getOfferingTokens() function has a business logic error which may lead users to get less weekly/yearly rewards. As shown in the following code snippets, the external function getOfferingTokens can only be called by the contract owner to get offering tokens (BNB-ETH) from auction lobby. However, if the contract owner calls this function more than one time to get offering tokens for a specified _vid, the calculations for vault.totalSupply (lines 681) and vault.totalSupply (lines 687) may not be correct. The vault.totalSupply value should be equal to the cumulative sum of the supply value returned by internally calling the auctionLobby.getOfferingTokens() function. The vault.allTotalSupply should be the sum of prevVault.allTotalSupply and vault.totalSupply().
```solidity
function getOfferingTokens(uint256 _vid, uint256 _aid) external onlyOwner returns (
    bool success,
    uint256 supply
) {
    VaultInfo storage vault = vaultInfo[_vid];
    (success, supply) = auctionLobby.getOfferingTokens(_aid, perCentOfAuctionTokens);
    if (success) {
        vault.totalSupply = supply;
        if (_vid == 0) {
            vault.allTotalSupply = supply;
        } else {
            VaultInfo storage prevVault = vaultInfo[_vid - 1];
            vault.allTotalSupply = prevVault.allTotalSupply + supply;
        }
    }
}
```

## Recommendation
Take into consideration the scenario where the contract owner may call the getOfferingTokens() function more than one time to get offering tokens for a specified _vid. An example revision is shown below:
```solidity
function getOfferingTokens(uint256 _vid, uint256 _aid) external onlyOwner returns (
    bool success,
    uint256 supply
) {
    VaultInfo storage vault = vaultInfo[_vid];
    (success, supply) = auctionLobby.getOfferingTokens(_aid, perCentOfAuctionTokens);
    if (success) {
        vault.totalSupply += supply;
        if (_vid == 0) {
            vault.allTotalSupply += supply;
        } else {
            VaultInfo storage prevVault = vaultInfo[_vid - 1];
            vault.allTotalSupply = prevVault.allTotalSupply + vault.totalSupply;
        }
    }
}
```
