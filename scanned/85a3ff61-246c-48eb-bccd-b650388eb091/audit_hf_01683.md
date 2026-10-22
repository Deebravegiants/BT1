# [M] updateBuffer() burns pxETH instead of institutional pxETH

## Summary
Severity: Medium
Contest weight: 0.4006
Dataset id: 9163
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In InstitutionalPirexEthConfigurationLogic.sol, batchBurnPxEth(), which is called by updateBuffer(), directly burns pxETH from all addresses specified in the burnerAccounts array:
```solidity
for (uint256 _i; _i < _len; ) {
    if (!burnerAccounts[_i].account)
        revert Errors.AccountNotApproved();
    _sum += burnerAccounts[_i].amount;
    burnPxEth();
}
```
However, since this is the institutional version of the protocol, it's not possible for any address to gain pxETH - depositing ETH through InstitutionalPirexEth.deposit() mints institutional pxETH to the caller, which cannot be unwrapped into apxETH unless you have the BURNER_ROLE. The only address that holds pxETH would be the AutoPxEth contract, which makes it impossible for governance to use burner accounts to compensate ETH.

## Recommendation
The function should burn institutional pxETH from burner accounts instead, by:
• Transferring institutional pxETH from the burner account to this contract.
• Unwrapping institutional pxETH into apxETH.
• Redeeming apxETH for pxETH and burning the received amount.
