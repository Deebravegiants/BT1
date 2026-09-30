# [M] Proper Fast Withdrawal Logic in _saveUserShares()

## Summary
Severity: Medium
Contest weight: 0.4217
Dataset id: 13044
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Spool protocol has a FastWithdraw contract that allows to withdraw user shares without the need to wait for the DoHardWork functions to be executed. The logic is to transfer the related withdrawal share to the FastWithdraw contract and the user can claim them later. Note that the performance fee is still paid to the vault where the shares where initially taken from. While analyzing the logic in the FastWithdraw contract, we notice there is a need to save user strategy shares that are being transfered from the vault as shown in the following routine. However, the logic blindly overwrites the internal state vaultWithdraw.proportionateDeposit, which may cause an issue if the user makes multiple consecutive fast withdraw requests!
```solidity
function _saveUserShares(
    address[] calldata vaultStrategies,
    uint128[] calldata sharesWithdrawn,
    uint256 proportionateDeposit,
    IVault vault,
    address user
) private {
    VaultWithdraw storage vaultWithdraw = userVaultWithdraw[user][vault];
    vaultWithdraw.proportionateDeposit = proportionateDeposit;
    for (uint256 i = 0; i < vaultStrategies.length; i++) {
        vaultWithdraw.userStrategyShares[vaultStrategies[i]] = sharesWithdrawn[i];
    }
}
```

## Recommendation
Properly revise the above routine to increase the state vaultWithdraw.proportionateDeposit by the given amount proportionateDeposit (line 186).
