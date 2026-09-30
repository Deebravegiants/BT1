# [M] The token balance of the ERC4626Router will return wrong balances for vaults with fees

## Summary
Severity: Medium
Contest weight: 0.4062
Dataset id: 5501
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function _tokenBalance(IERC20 token) public view returns (uint balance) {
    balance = token.balanceOf(address(this));
    IERC4626 vault = vaults[token];
    if (address(vault) != address(0)) {
        balance += vault.convertToAssets(vault.balanceOf(address(this)));
    }
}
```
The _tokenBalance in the ERC4626Router is used to return the balance of a token hold by the router, this is computed by getting the balance of the router and the number of assets hold by the router in the the token's vault by calling convertToAssets: The problem with this is that if the vault has fees on withdraw, the convertToAssets will not take that into consideration according to the EIP, this will result in untruthful balance returned by this function.  
convertToAssets  
Must NOT include any fees that are charged against assets in the vault.

## Recommendation
Consider using previewRedeem as this should return the closes number of assets that would be received if redeem would have been called.  
previewRedeem  
MUST return as close to and no more than the exact amount of assets that would be withdrawn in a redeem call in the same transaction. I.e. redeem should return the same or more assets as previewRedeem if called in the same transaction.
