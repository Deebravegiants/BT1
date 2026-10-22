# [H] Attribute Change Bug

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23362
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The compliance system maintains several count variables (accreditedInvestorsCount, usAccreditedInvestorsCount, euRetailInvestorsCount, between others) to enforce investor limits and regulatory compliance. However, when investor attributes are changed through setAttribute() or updateInvestor() functions, these count variables are not updated to reflect the changes.  
The system only updates counts when investors are added or removed via adjustInvestorCountsAfterCountryChange(), but attribute changes that affect investor classification (ACCREDITED, QUALIFIED) bypass this mechanism entirely. This creates a fundamental disconnect between the actual investor status and the compliance tracking system.  

This affect specifically accreditedInvestorsCount, usAccreditedInvestorsCount, euRetailInvestorsCount for example:  

```solidity
} else if (countryCompliance == EU && !getRegistryService().isQualifiedInvestor(_id)) {//@audit if
there are an investor that become qualified after he enter the system counting it will not be
discounting the investor when he is leaving
,!
,!
if(_increase == CommonUtils.IncDec.Increase) {
    euRetailInvestorsCount[_country]++;
}
else {
    euRetailInvestorsCount[_country]--;
}
```

In this case if EU retail investor enter the system he will count in euRetailInvestorsCount but if he become QUALIFIED and then leave the system the euRetailInvestorsCount will remain inflated.  

Impact: investor limit enforcement becomes unreliable as counts don't reflect actual count.

## Proof of Concept
```typescript
describe('Proof of Concept: Attribute Change Bug', function () {
    it('should demonstrate euRetailInvestorsCount inflation when investor becomes qualified', async function () {
        const [wallet, wallet2, transferAgent] = await hre.ethers.getSigners();
        const { dsToken, registryService, complianceService, complianceConfigurationService, trustService } = await loadFixture(deployDSTokenRegulated);
        // Set up EU compliance
        await complianceConfigurationService.setCountryCompliance(INVESTORS.Country.FRANCE, INVESTORS.Compliance.EU);
        await complianceConfigurationService.setEURetailInvestorsLimit(1);
        // Register two investors in France
        await registerInvestor(INVESTORS.INVESTOR_ID.INVESTOR_ID_1, wallet, registryService);
        await registerInvestor(INVESTORS.INVESTOR_ID.INVESTOR_ID_2, wallet2, registryService);
        // Set both investors to France (EU)
        await registryService.setCountry(INVESTORS.INVESTOR_ID.INVESTOR_ID_1, INVESTORS.Country.FRANCE);
        await registryService.setCountry(INVESTORS.INVESTOR_ID.INVESTOR_ID_2, INVESTORS.Country.FRANCE);
        // Issue tokens to first investor (non-qualified) - should be counted as EU retail
        await dsToken.issueTokens(wallet, 100);
        // Check initial EU retail count
        const initialEuRetailCount = await complianceService.getEURetailInvestorsCount(INVESTORS.Country.FRANCE);
        expect(initialEuRetailCount).to.equal(1, "Initial EU retail count should be 1");
        // Try to issue tokens to second investor - should fail due to EU retail limit
        await expect(dsToken.issueTokens(wallet2, 100)).revertedWith('Max investors in category');
        // Now make the first investor qualified via setAttribute
        // QUALIFIED = 4, APPROVED = 1
        await registryService.setAttribute(INVESTORS.INVESTOR_ID.INVESTOR_ID_1, 4, 1, 0, "");
        // Check EU retail count - it should still be 1 (BUG: should be 0)
        const euRetailCountAfterQualification = await complianceService.getEURetailInvestorsCount(INVESTORS.Country.FRANCE);
        expect(euRetailCountAfterQualification).to.equal(1, "BUG: EU retail count should be 0 after qualification, but it's still 1");
        // Now try to issue tokens to second investor - this should still fail due to inflated count
        await expect(dsToken.issueTokens(wallet2, 100)).revertedWith('Max investors in category');
    });
});
```

## Recommendation
Recommended Mitigation: Ensure that any attribute change that affects investor classification immediately updates the corresponding compliance count variables to maintain system integrity.
