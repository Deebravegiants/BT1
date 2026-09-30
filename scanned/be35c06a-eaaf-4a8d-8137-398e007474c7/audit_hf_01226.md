# [M] Missing slippage checks on deposits and withdrawals could result in sandwich attacks

## Summary
Severity: Medium
Contest weight: 0.4602
Dataset id: 5511
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
It is a known issue that ERC4626 deposit and withdrawal operations lack slippage checks. The EIP does not enforce them, leaving it to integrators to ensure slippage checks are implemented whenever a deposit or withdrawal is performed. Every deposit or withdrawal creates an opportunity for MEV by manipulating the share price, which can result in fewer shares or assets being received by the vault. A good example where slippage can cause significant damage is the setVaultForToken function. The router's admin can set or change a vault for a specific token by calling this function.  
The flow is as follows:  
1. Suppose the router currently holds an oldVault for a token T and has "shares" of that vault.  
2. When an admin calls setVaultForToken(T, newVault), the code:  
   1. Redeems 100% of the shares from oldVault into the underlying token T.  
   2. Sets vaults[T] = newVault.  
   3. Deposits all token T holdings into the newly assigned vault.  
Since both _deposit and redeem lack slippage checks, they can be easily exploited through MEV. The above flow can be summarized as:  
• Redeem up to oldVault.maxRedeem(...) shares.  
• Deposit all resulting token T holdings into newVault.  
If the share prices of the old and new vaults can be manipulated, an attacker could sandwich the change, causing the vault to withdraw fewer assets and deposit even less. This is possible by decreasing the share price during redemption from the old vault and increasing it during the deposit into the new vault.  
This issue currently has a medium impact because the planned deployment is only for Arbitrum and Base, which do not have a public mempool, making exploitation less frequent. However, accidental MEV is still possible.
```solidity
function setVaultForToken(IERC20 token, IERC4626 vault) public virtual onlyAdmin {
    // Verify that the token is not the zero address
    require(address(token) != address(0), "ERC4626Router/zeroToken");
    // If a previous vault exists, withdraw all assets
    IERC4626 oldVault = vaults[token];
    if (address(oldVault) != address(0)) {
        uint shares = oldVault.balanceOf(address(this));
        if (shares > 0) {
            uint maxRedeemable = oldVault.maxRedeem(address(this));
            require(maxRedeemable >= shares, "ERC4626Router/maxRedeemExceeded");
            oldVault.redeem(maxRedeemable < shares ? maxRedeemable : shares, address(this), address(this));
        }
    }
    // Set the new vault
    vaults[token] = vault;
    // Re-deposit the token
    _deposit(token);
}
```

## Recommendation
Consider adding slippage checks throughout the router for both deposit and withdrawal operations from the vault.
