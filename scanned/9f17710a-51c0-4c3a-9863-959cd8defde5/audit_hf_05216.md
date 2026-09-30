# [H] Asymmetry enforcement between TokenIssuer::registerInvestor, WalletRegistrar::registerWallet and SecuritizeSwap::_registerNewInvestor

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23361
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In TokenIssuer::registerInvestor, if the user isn't already an investor they get registered and must have 3 specific attributes set:

```solidity
if (!getRegistryService().isInvestor(_id)) {
    getRegistryService().registerInvestor(_id, _collisionHash);
    getRegistryService().setCountry(_id, _country);
    if (_attributeValues.length > 0) {
        require(_attributeValues.length == 3, "Wrong length of parameters");
        getRegistryService().setAttribute(_id, KYC_APPROVED, _attributeValues[0],
            _attributeExpirations[0], "");
        getRegistryService().setAttribute(_id, ACCREDITED, _attributeValues[1],
            _attributeExpirations[1], "");
        getRegistryService().setAttribute(_id, QUALIFIED, _attributeValues[2],
            _attributeExpirations[2], "");
    }
}
```

But in WalletRegistrar::registerWallet and SecuritizeSwap::_registerNewInvestor if the user isn't already an investor, they get registered but the same attribute logic is not there. Instead it is more generic appearing to over‑write anything that exists and not enforcing existence of `KYC_APPROVED`, `ACCREDITED` or `QUALIFIED` attributes:

```solidity
if (!registryService.isInvestor(_id)) {
    registryService.registerInvestor(_id, _collisionHash);
    registryService.setCountry(_id, _country);
}
for (uint256 i = 0; i < _wallets.length; i++) {
    if (registryService.isWallet(_wallets[i])) {
        require(CommonUtils.isEqualString(registryService.getInvestor(_wallets[i]), _id), "Wallet belongs to a different investor");
    } else {
        registryService.addWallet(_wallets[i], _id);
    }
}
for (uint256 i = 0; i < _attributeIds.length; i++) {
    registryService.setAttribute(_id, _attributeIds[i], _attributeValues[i], _attributeExpirations[i], "");
}
```

Impact: Going through `WalletRegistrar::registerWallet` or `SecuritizeSwap::_registerNewInvestor` an investor can be registered without the required attributes.

## Recommendation
Recommended Mitigation: Harmonize the investor registration process to remove duplicated code and enforce the same requirements.
