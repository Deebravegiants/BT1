# [M] 5.3.8 Possible mismatch betweenValidator.countandAeraVaultassets count

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** PermissiveWithdrawalValidator.sol#L13, AeraVaultV1.sol#L456-L
**Description:** A weak connection betweenWithdrawalValidatorandAera Vaultcould lead to the inability of
withdrawing from a Vault.
Consider the following scenario:
The Validator is deployed with atokenCount< thanVault.getTokens().length. Inside thewithdraw()function
we reference the following code block:
uint256[] memory allowances = validator.allowance();
uint256[] memory weights = getNormalizedWeights();
uint256[] memory newWeights = new uint256[](tokens.length);
for (uint256 i = 0; i < tokens.length; i++) {
if (amounts[i] > holdings[i] || amounts[i] > allowances[i]) {
revert Aera__AmountExceedAvailable(
address(tokens[i]),
amounts[i],
holdings[i].min(allowances[i])
);
}
}

A scenario whereallowances.length < tokens.lengthwould cause this function to revert with an Index out of
bounds error. The only way for the Treasury to withdraw funds would be via thefinalize()method which has a
time delay.
**Recommendation:** Ensure that whenAera VaultandValidatorare deployed,Validator.countis the same
as the number of assets managed by the vault.
A potential solution is to create a Factory contract that will deploy both theAera Vaultand theValidator. In
such case remember to correctly set up theAera VaultOwnable contract because the current deployer is also
the Vault’s owner and in the case of a Factory, the owner of the vault would be the Factory itself. This would cause
allonlyOwnercalls to revert.
Additionally, see the following issue:Ensure integrity of deployment of vault.
**Gauntlet:** I think we are ok with trusting the treasury to deploy the validator. The main reason being is that we
don’t see a simple way to parametrize validators at the moment and each treasury partner will be highly trusted
early on so we’d be starting with permissive validators and then leaning on treasuries to suggest some custom
validators first.
Checked onallowances.lengthadded in PR #141.
**Spearbit:** Acknowledged.
