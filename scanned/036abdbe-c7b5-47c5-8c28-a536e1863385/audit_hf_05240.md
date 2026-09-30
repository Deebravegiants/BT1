# [H] Seized tokens are stuck on the receiver

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23413
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When seizing DSTokens, the receiver of the confiscated assets must be an issuer wallet. A wallet that is an issuer wallet must not be an investor wallet. This means the receiver wallet won't point to an investor, so reading `getRegistryService().getInvestor(_wallet);` would return an empty string.  

This has the side effect that during the seizure of funds, when updating the `investorsBalance` of the wallet receiving the confiscated funds won't register any `investorsBalance` because there is not an investor associated to that wallet.  

```solidity
function seize(
    TokenData storage _tokenData,
    address[] memory _services,
    address _from,
    address _to,
    uint256 _value,
    uint256 _shares
)
    public
    validSeizeParameters(_tokenData, _from, _to, _shares)
{
    ...
    @> updateInvestorBalance(_tokenData, registryService, _to, _shares, CommonUtils.IncDec.Increase);
}
```

```solidity
function updateInvestorBalance(
    TokenData storage _tokenData,
    IDSRegistryService _registryService,
    address _wallet,
    uint256 _shares,
    CommonUtils.IncDec _increase
) internal returns (bool) {
    //! @audit => investor for the wallet receiving the seized funds would return an empty string
    string memory investor = _registryService.getInvestor(_wallet);
    //! @audit => An empty string would skip the code to register the investorsBalance for the seized funds
    if (!CommonUtils.isEmptyString(investor)) {
        uint256 balance = _tokenData.investorsBalances[investor];
        if (_increase == CommonUtils.IncDec.Increase) {
            balance += _shares;
        } else {
            balance -= _shares;
        }
        _tokenData.investorsBalances[investor] = balance;
    }
    return true;
}
```

Not having an `investorsBalance` for the seized funds means that `InvestorLockManager.getTransferableTokens()` will return `0` available tokens to be transferred when attempting to move the seized funds.  

```solidity
function completeTransferCheck(
    address[] memory _services,
    CompletePreTransferCheckArgs memory _args
) internal view returns (uint256 code, string memory reason) {
    ...
    if (
        !isPlatformWalletFrom &&
        @> IDSLockManager(_services[LOCK_MANAGER]).getTransferableTokens(_args.from, block.timestamp) < _args.value,
    ) {
        @> return (16, TOKENS_LOCKED);
    }
}
```

**Impact:** Seized tokens won't be transferable from the address receiving the confiscated funds.

## Proof of Concept
```typescript
it.only('seized tokens are stuck on the receiver', async function () {
    const [owner, investor1, investor2, seizedReceiver, investor3] = await hre.ethers.getSigners();
    const { dsToken, registryService, complianceService, complianceConfigurationService,
        walletManager } = await loadFixture(deployDSTokenRegulated);
    await complianceConfigurationService.setCountryCompliance(INVESTORS.Country.FRANCE,
        INVESTORS.Compliance.EU);
    await complianceConfigurationService.setCountryCompliance(INVESTORS.Country.USA,
        INVESTORS.Compliance.US);
    await complianceConfigurationService.setEURetailInvestorsLimit(10);
    await registerInvestor(INVESTORS.INVESTOR_ID.INVESTOR_ID_1, investor1, registryService);
    await registerInvestor(INVESTORS.INVESTOR_ID.INVESTOR_ID_2, investor2, registryService);
    // await registerInvestor(INVESTORS.INVESTOR_ID.US_INVESTOR_ID, seizedReceiver, registryService);
    await registerInvestor(INVESTORS.INVESTOR_ID.US_INVESTOR_ID_2, investor3, registryService);
    await registryService.setCountry(INVESTORS.INVESTOR_ID.INVESTOR_ID_1, INVESTORS.Country.FRANCE);
    await registryService.setCountry(INVESTORS.INVESTOR_ID.INVESTOR_ID_2, INVESTORS.Country.USA);
    // await registryService.setCountry(INVESTORS.INVESTOR_ID.US_INVESTOR_ID, INVESTORS.Country.USA);
    await registryService.setCountry(INVESTORS.INVESTOR_ID.US_INVESTOR_ID_2, INVESTORS.Country.USA);
    const issuedTokens = 500;
    const seizedTokens = issuedTokens;
    await dsToken.issueTokens(investor1, issuedTokens);
    await dsToken.issueTokens(investor2, issuedTokens);
    expect(await complianceService.getEURetailInvestorsCount(INVESTORS.Country.FRANCE)).equal(1);
    expect(await complianceService.getUSInvestorsCount()).equal(1);
    await walletManager.addIssuerWallet(seizedReceiver)
    await dsToken.seize(investor1, seizedReceiver, await
        dsToken.balanceOfInvestor(INVESTORS.INVESTOR_ID.INVESTOR_ID_1), "");
    expect(await dsToken.balanceOfInvestor(INVESTORS.INVESTOR_ID.INVESTOR_ID_1)).equal(0);
    expect(await dsToken.balanceOf(investor1)).equal(0);
    expect(await complianceService.getEURetailInvestorsCount(INVESTORS.Country.FRANCE)).equal(0);
    expect(await complianceService.getUSInvestorsCount()).equal(1);
    expect(await dsToken.balanceOf(seizedReceiver)).equal(500);
    time.increase(10_000);
    const dsTokenFromSeizedReceiver = await dsToken.connect(seizedReceiver);
    //@audit-issue => Seized tokens will be stuck on the receiver of the seized funds because it is
    // not an investor and never receives investorsBalance,
    await expect(dsTokenFromSeizedReceiver.transfer(investor3, seizedTokens)).to.be.reverted;
});
```

## Recommendation
Information not provided
