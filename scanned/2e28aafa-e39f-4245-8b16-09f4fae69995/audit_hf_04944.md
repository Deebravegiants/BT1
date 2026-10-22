# [M] If the accounted token balance is higher than

## Summary
Severity: Medium
Contest weight: 0.2523
Dataset id: 22893
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In extreme cases, such as when late liquidations incur losses to liquidity providers, the actual balance will not exist in the vaults. The transfer will not revert due to how remains unchanged. This will lead to insolvency. When tokens are insufficient in the vaults, the token amount might never be sent to the users/pools without a revert.

For example, in cases of late liquidation during extreme market conditions, closing the liquidated positions will update the corresponding storage balances in pools and vaults. However, if there are insufficient funds in the pool, the tokens are not transferred to their destination, and the amount not sent is not checked. As seen in the DecreasePositionProcess::_settleCrossAccount and _settleIsolateAccount functions, VaultProcess.transferOut is called with the boolean set to "true," which will skip the token transfer if the contract's token balance is insufficient.

Consequently, the tokens are assumed to be sent in the exact amount reflected in the storage variables. However, the actual tokens transferred (0) can be significantly different, leading to insolvency.

This is definitely a problem in extreme market conditions where the pool incurs losses from undercollateralized borrowed positions or very high funding fees. In such cases, closing positions will not be tracked, and the actual balance transferred might be "0" for some users because there are not enough tokens in the vault. Since this would require a volatile market for the asset, I will label this as medium.

a04d794bf6b8104528681ad/elfi-perp-contracts/contracts/process/VaultProcess.sol#L13-L31  
a04d794bf6b8104528681ad/elfi-perp-contracts/contracts/vault/Vault.sol#L16-L2  
a04d794bf6b8104528681ad/elfi-perp-contracts/contracts/process/DecreasePositionProcess.sol#L338-L444  
a04d794bf6b8104528681ad/elfi-perp-contracts/contracts/process/IncreasePositionProcess.sol#L83-L104  
a04d794bf6b8104528681ad/elfi-perp-contracts/contracts/process/MarketProcess.sol#L118-L126

## Recommendation
Also check what's transferred and if there is a leak account it. Also, if the users requested is not enough instead of not sending any tokens send the existing balance OR socialize the losses in such cases and make sure no account can close their position without incurring the loss.
