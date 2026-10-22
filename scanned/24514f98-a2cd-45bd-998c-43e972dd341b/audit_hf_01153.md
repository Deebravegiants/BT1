# [M] Superform protocol doesn't support vaults if their underlying asset is a fee-on-transfer type token

## Summary
Severity: Medium
Reporter: hals, also found by pks271, 8olidity and Mario Poneder
Contest weight: 0.4110
Dataset id: 4920
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol allows any vault owner from adding their vaults to the protocol by wrapping them to one of the approved form implementations. These vaults can have any type of underlying assets including fee-on-transfer token type; which deducts a fee from the transferred amount, so the resulting final balance of the receiver would be less than the sent amount by the amount of the deducted fees. It was noticed that the protocol doesn't support such type of tokens; users can't deposit in vaults with fee-on-transfer tokens due to this check made in the ERC4626FormImplementation._processDirectDeposit function
```solidity
vars.assetDifference = IERC20(vars.asset).balanceOf(address(this)) - vars.balanceBefore;
/// @dev the difference in vault tokens, ready to be deposited, is compared with the amount inscribed in the
/// superform data
if (vars.assetDifference < singleVaultData_.amount) {
    revert Error.DIRECT_DEPOSIT_INVALID_DATA();
}
```
where vars.assetDifference will always be less than singleVaultData_.amount due to the deducted fees (for fee-on-transfer underlying vault token).

## Recommendation
No data
