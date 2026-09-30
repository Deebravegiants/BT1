# [M] Returning Funds when totalShares is Zero May Lead to Denial of Service & Lock Funds

## Summary
Severity: Medium
Contest weight: 0.1106
Dataset id: 14456
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Due to the lack of check for the totalShares in function returnFunds(), the _currentExchangeRate can be updated to zero, which causes Denial of Service and lock of funds.
Function returnFunds() allows any users to return tokens to the system which will alter the exchange rate. When the totalShares == 0 and a user calls the returnFunds() function, the exchange rate will be set to zero on line [338]. As a result, no StakedToken will be minted for new stakers, and hence, stakers cannot redeem their tokens and the funds will be locked in the contract.
Furthermore, the function slash() cannot be called due to a division by zero issue in previewRedeem() in line [318]. Hence, Denial of Service occurs.

## Recommendation
Add a require statement in function returnFunds() to prevent calling this function when totalShares is zero.
