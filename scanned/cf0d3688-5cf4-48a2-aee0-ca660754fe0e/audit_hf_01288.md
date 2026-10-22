# [M] The info function in the AgreementStaking will run out of gas

## Summary
Severity: Medium
Contest weight: 0.4043
Dataset id: 6068
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function info()
    external
    view
    override
    returns (Metadata memory metadata, Whitelist memory whitelist)
{
    Storage storage $ = _storage();
    (metadata.leverage, metadata.totalDepositThreshold, metadata.apy) = _info();
    metadata.collaterals = $.collaterals.values();
    metadata.lenders = _getRoleMembers(LENDER_ROLE);
    metadata.borrowers = _getRoleMembers(BORROWER_ROLE);
    IWhitelistingControllerAgreement wc = IWhitelistingControllerAgreement(compliance);
    whitelist = Whitelist(wc.getTokens(address(this)), wc.getOperators(address(this)));
    return (metadata, whitelist);
}
```
The problem is that as the list of borrowers and lenders grows, the function may eventually exceed the gas limit and revert. This issue becomes serious as its used in the ThresholdsVerifier.verifyThresholds which will result in DoSing the veriﬁcation.

## Recommendation
Consider splitting this into another function that gets only the metadata without lenders/borrowers so that could be used in the ThresholdsVerifier without DoSing and a function that can be called offchain which could return everything.
