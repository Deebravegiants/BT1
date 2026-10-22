# [M] Total coverage is not reduced in Vault.claim()

## Summary
Severity: Medium
Contest weight: 0.4099
Dataset id: 15255
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a Validator is slashed, the user that has covered that Validator can call Vault.claim() and receive a coverage payout. The issue is that the state variable vaultStorage.state.totalCoverage is not reduced by coverage. However, vaultStorage.state.totalUnderWriterEth and vaultStorage.state.totalUnderWriterToken are reduced, which means future users might be unable to purchase coverage since Vault.purchase() might revert unexpectedly since vaultStorage.state.totalCoverage has an inflated value and the check for enough available funds for coverage might fail.
# Vault.sol
```solidity
function purchase(
uint256 _coverage,
) external payable nonReentrant onlyNonZero(premium) WhenNotPaused WhenVaultNotExpired {
if (
totalPossibleCoverage * vaultStorage.config.leverageBasisPoints / basisPtsToDecimal
< vaultStorage.state.totalCoverage + _coverage
) {
revert NotEnoughFundsForCoverage();
}
vaultStorage.state.totalCoverage += _coverage;
}
```

## Recommendation
```diff
@@ -292,6 +293,7 @@ contract Vault is
vaultStorage.state.totalUnderWriterToken -= amountOfToken;
vaultStorage.state.totalUnderWriterEth -= amountOfEth;
+
vaultStorage.state.totalCoverage -= vaultStorage.state.coveredValidators[claimParams.validatorIndex].coverage;
// paying out underwriterTokens
```
