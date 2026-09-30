# [H] ComplianceServiceRegulated::preIssuanceCheck allows issuance to non-accredited investors

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23406
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
ComplianceServiceRegulated::completeTransferCheck has several checks that preIssuanceCheck is missing:
1) Force Accredited
completeTransferCheck verifies whether force accredited is enabled and if so only allow transfers to accredited investors:
```solidity
bool isAccreditedTo = isAccredited(_services, _args.to);
if (
    IDSComplianceConfigurationService(_services[COMPLIANCE_CONFIGURATION_SERVICE]).getForceAccredited()
    && !isAccreditedTo,!
) {
    return (61, ONLY_ACCREDITED);
}
} else if (toRegion == US) {
    if (
        IDSComplianceConfigurationService(_services[COMPLIANCE_CONFIGURATION_SERVICE]).getForceAccredit c
        edUS() &&,!
        !isAccreditedTo
    ) {
        return (62, ONLY_US_ACCREDITED);
    }
```
But preIssuanceCheck doesn't enforce this, so it could allow issuance to unaccredited investors even when
ForceAccredited or ForceAccreditedUS is enabled.
2) Regional Minimal Token Holdings
completeTransferCheck verifies regional minimum token holdings eg:
```solidity
if (toInvestorBalance + _value <
    IDSComplianceConfigurationService(_services[COMPLIANCE_CONFIGURATION_SERVICE]).getMinUSTokens()) {,!
    return (51, AMOUNT_OF_TOKENS_UNDER_MIN);
}
```
But preIssuanceCheck only verifies the generic minimum holdings:
```solidity
if (
    !walletManager.isPlatformWallet(_to) &&
    balanceOfInvestorTo + _value < complianceConfigurationService.getMinimumHoldingsPerInvestor()
) {
    return (51, AMOUNT_OF_TOKENS_UNDER_MIN);
}
```
Hence preIssuanceCheck could result in users being issued an amount of tokens that violates their regional
minimum token holdings.

## Recommendation
Enforce the above checks in ComplianceServiceRegulated::preIssuanceCheck.
