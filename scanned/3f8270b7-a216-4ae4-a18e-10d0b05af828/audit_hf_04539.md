# [M] M-19 | Usage Of DEFAULT Price Tolerance

## Summary
Severity: Medium
Contest weight: 0.1572
Dataset id: 22103
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
getCurrentPrice from PerpsPrice.sol has a different staleness tolerances for different cases. In the
current cannon deployment, node's DEFAULT tolerance is settled as 1 hour.
Using a 1 hour price tolerance might lead to some attack vectors because user can maliciously
choose best price for their purpose from the last one hour to use.
Followings are some functions that uses DEFAULT tolerance and possible attack vectors that can be
used with them:
1. minimumCredit : This can be used to bypass checks (withdrawing collateral from market as an LP
when the minimumCredit is in the border)
2. isEligibleForLiquidation : Accounts that are liquidatable can settle order via bypassing this check.
3. reportedDebt : Can return not accurate values
4. View functions: Might be problematic for integrators.
The reason for decreased severity is because it requires no recent update in Pyth price within the
time period and because in order to create a large enough impact it requires good amount of price
change within one hour window.

## Recommendation
Be more strict for DEFAULT tolerance to decrease the possibility of mentioned issues and if possible
use STRICT tolerance for specified functions. Also be sure to inform integrators about possible
deviations if STRICT tolerance is not gonna be used for view functions.
