# [M] 5.3.1 transfer(...)function in_issuePayout(...)can be replaced by a directcall.

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:**

- VaultImplementation.sol#L245
**Description:** In the_issuePayout(...) internal function of theVaultImplementationif the asset isWETHthe
amount is withdrawn fromWETHto native tokens and thentransfered to theborrower:
if (asset() == WETH()) {
IWETH9 wethContract = IWETH9(asset());
wethContract.withdraw(newAmount);
payable(borrower).transfer(newAmount);
}

transferlimits the amount of gas shared to the call to theborrowerwhich would prevent executing a complex
callback and due to changes in gas prices inEVMit might even break some feature for a potentialborrowercontract.
For the analysis of the flow for both types of vaults please refer to the following issue:

- 'Storage parameters are updated after a few callback sites to external addresses in the commitToLien(...)
    flow'
**Recommendation:** callthe borrower directly without restricting the gas shared and only apply this recommen-
dation if the recommendation from issue'Storage parameters are updated after a few callback sites to external
addresses in the commitToLien(...) flow'is applied.
