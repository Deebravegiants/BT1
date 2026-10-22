# [H] Burn and seize functions can be DoS when investor has several wallets that they control

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23368
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: The burn function in TokenLibrary.sol checks walletsBalances[_who] (individual wallet balance,
see the arrow above) instead of investorsBalances[investorId] (total investor balance across all wallets). This
allows investors with multiple registered wallets to make their tokens unburnable by transferring tokens between
their own wallets.

```solidity
function burn(
    TokenData storage _tokenData,
    address[] memory _services,
    address _who,
    uint256 _value,
    ISecuritizeRebasingProvider _rebasingProvider
) public returns (uint256) {
    uint256 sharesToBurn = _rebasingProvider.convertTokensToShares(_value);
    require(sharesToBurn <= _tokenData.walletsBalances[_who], "Not enough balance"); <---------
    IDSComplianceService(_services[COMPLIANCE_SERVICE]).validateBurn(_who, _value);
    _tokenData.walletsBalances[_who] -= sharesToBurn;
    updateInvestorBalance(
        _tokenData,
        IDSRegistryService(_services[REGISTRY_SERVICE]),
        _who,
        sharesToBurn,
        CommonUtils.IncDec.Decrease
    );
    _tokenData.totalSupply -= sharesToBurn;
    return sharesToBurn;
}
```

When an investor transfers tokens from their original wallet to another wallet they control, the burn function will fail
with "Not enough balance" even though the investor still owns the tokens in their total balance.

## Proof of Concept
```typescript
describe('Burn DoS Vulnerability POC', function() {
    it('Should demonstrate that burn can be DoS by transferring between investor wallets', async
    function() {,!
        const [investor, wallet2, wallet3] = await hre.ethers.getSigners();
        const { dsToken, registryService } = await
        loadFixture(deployDSTokenRegulatedWithRebasingAndEighteenDecimal);,!
        // Register investor with multiple wallets
        await registerInvestor(INVESTORS.INVESTOR_ID.INVESTOR_ID_1, investor.address,
        registryService);,!
        await registryService.addWallet(wallet2.address, INVESTORS.INVESTOR_ID.INVESTOR_ID_1);
        await registryService.addWallet(wallet3.address, INVESTORS.INVESTOR_ID.INVESTOR_ID_1);
        // Issue tokens to investor
        await dsToken.issueTokens(investor.address, 1000);
        // Transfer tokens between investor's own wallets
        await dsToken.connect(investor).transfer(wallet2.address, 1000);
        45
        // Now investor has 0 balance in original wallet but 1000 total
        expect(await dsToken.balanceOf(investor.address)).to.equal(0);
        expect(await dsToken.balanceOfInvestor(INVESTORS.INVESTOR_ID.INVESTOR_ID_1)).to.equal(1000);
        // VULNERABILITY: Burn fails because wallet balance is 0, even though investor has tokens
        await expect(dsToken.burn(investor.address, 100, 'DoS test'))
        .to.be.revertedWith('Not enough balance');
    });
});
```

## Recommendation
Recommended Mitigation: Possible mitigation options include:
• perform sensitive admin transactions such as burn and seize through private mempool services like flashbots
so they can't be front‑run  
• remove the addWalletByInvestor function to prevent investors from continually adding more wallets and
distributing their tokens to them  
• add burnAll and seizeAll functions to DSToken which iterate over every wallet belonging to an investor and
burn/seize all their tokens
