# [M] Unsafe casting to uint88

## Summary
Severity: Medium
Contest weight: 0.1533
Dataset id: 17644
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
fCashAmount is unsafely casted to uint88 in when buying and selling collateral in VaultFCActions.sol.  
In both buying and selling collateral, the respective functions take fCashAmount as uint256. It is unsafely casted to uint88 in the _buyFCash() and _sellFCash() functions.  
Even though _sellfCash() checks for the casting overflow, the casting has already performed, making it redundant.  
The deltaCollateral calculated would be impacted as it retains the original value that could exceed type(uint88).max. As a POC, if we take fCashAmount to be type(uint88.max) + 1, we would have vastly different values for deltaCollateral and fCashAmount:  
• deltaCollateral = 3094850098213450687247810560000000000  
• fCashAmount = 0  
The collateral to be credited / deducted can be made to be much greater / smaller than the fCashAmount. The likelihood of an exploit is low, because the collateral has to be transferred into and from the vault, which, in practice, would be too large an amount for most collateral tokens.

## Recommendation
The _buyFCash() and _sellFCash() functions should take in fCashAmount as a uint256 instead of uint88. The _buyFCash() should have the overflow check as well.  
Fix: https://github.com/fiatdao/actions/pull/13
