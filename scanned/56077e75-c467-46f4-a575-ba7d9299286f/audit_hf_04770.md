# [M] Incorrect decimal handling inside _compoundInterest

## Summary
Severity: Medium
Contest weight: 0.5857
Dataset id: 22617
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Incorrect decimal handling inside _compoundInterest function makes the protocol lose fees  
```solidity
function _compoundInterest() internal {
    uint256 lenderBalanceBefore = uint256(s_assetData.lenderBalance);
    if (lenderBalanceBefore > 0 && s_isActive) {
        uint256 compoundedInterest = MathUtils.calculateCompoundedInterest(
            uint256(s_terms.interestRate).wadToRay(),
            s_assetData.interestLastUpdatedAt, block.timestamp
        ).rayToWad();
        s_assetData.lenderBalance =
            lenderBalanceBefore.wadMul(compoundedInterest).toUint216();
        uint256 earnedFeeAmount =
            uint256(s_terms.interestFee).wadMul(s_assetData.lenderBalance - lenderBalanceBefore);
        uint256 feeShareAmount =
            totalSupply(LENDER_LP_TOKEN_ID).wadMul(earnedFeeAmount).wadDiv(
                s_assetData.lenderBalance - earnedFeeAmount
            );
    }
}
```
Here in case the token's decimals are low (usdc,wbtc) then the multiplication totalSupply(LENDER_LP_TOKEN_ID).wadMul(earnedFeeAmount) will result in 0 in a lot of ranges (until totalSupply * earnedFeeAmount reaches 1e18 which is dependent on other factors like the interest rate,fee, time between calls etc but in most normal scenarios would result in < 1e18 unless totalSupply, which has the same decimals as the token, is really large). Hence the protocol will lose out on fees  
Eg: balance = totalSupply == 1e5 * e6 compoundedInterest = 1.0001e18 // 0.01% hence new balance = 100010000000 protocolFee = 0.01e18 // 1% hence earned fee = 100000  
feeShareAmount = (1e11 * (1e5) / 1e18) * .... == 0  
with correct ordering = ((1e5 * 1e18 / (100010000000 - 100000) ) * (1e11)) / 1e18 == 99990  
Protocol will lose out on fees

## Recommendation
Rearrange div and mul as follows:  
```solidity
uint256 feeShareAmount = (earnedFeeAmount).wadDiv(
    s_assetData.lenderBalance - earnedFeeAmount
).wadMul(totalSupply(LENDER_LP_TOKEN_ID));
```
