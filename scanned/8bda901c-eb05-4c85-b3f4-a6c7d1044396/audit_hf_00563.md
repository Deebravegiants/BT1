# [H] H-02 | ExitVaultEntryPoint.transferFrom Can Be Abused By The Vault Owner To Prevent A User From Withdrawing

## Summary
Severity: High
Contest weight: 0.5984
Dataset id: 2025
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The transferFrom function in the ExitVaultEntryPoint contract allows the vault owner to transfer ownership of the vault to another user. However, this can be abused to prevent a user from completing their withdrawals. The issue happens when the initial owner fully completes their withdrawal and then transfers their ownership/NFT. As the initial vault owner had withdrawn all his funds at this point, s.ownerInitialGMX and s.ownerInitialGLP will be zero, leading to an underflow when the new owner attempts to complete the withdrawal of his shares in the matchWithdrawRequest function:
```solidity
function matchWithdrawRequest(address _staker, address _token, uint256 _fillAmount, uint256 _minDonation)
external checkFullPausedVault {
    // Update the new staker UserInfo.
    if (_token == TOKEN_GMX) {
        _depositGMX(0, _staker);
        // Claims rewards
        stakerInfo.gmxStream.shares = totalShares;
        matcherInfo.gmxStream.shares = totalShares;
        if (_staker == s.owner) s.ownerInitialGMX = totalShares; <--------
    } else {
        _depositGLP(0, _staker);
        // Claims rewards
        stakerInfo.glpStream.shares = totalShares;
        matcherInfo.glpStream.shares = totalShares;
        if (_staker == s.owner) s.ownerInitialGLP = totalShares; <--------
    }
}
```

## Recommendation
Under the current implementation the s.ownerInitialGMX and s.ownerInitialGLP state variables do not add any functionality to the contracts except this restriction that can be abused this way. Consider removing them.
