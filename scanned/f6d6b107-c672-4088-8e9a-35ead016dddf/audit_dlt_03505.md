# [M] Centralisation Risk: Admin Can Change Important Variables To Steal Funds

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-06-illuminate
Published: 2022-06-23
Source: https://github.com/code-423n4/2022-06-illuminate-findings/issues/44
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-06-illuminate/blob/912be2a90ded4a557f121fe565d12ec48d0c4684/lender/Lender.sol#L78
https://github.com/code-423n4/2022-06-illuminate/blob/912be2a90ded4a557f121fe565d12ec48d0c4684/lender/Lender.sol#L107
https://github.com/code-423n4/2022-06-illuminate/blob/912be2a90ded4a557f121fe565d12ec48d0c4684/lender/Lender.sol#L137
https://github.com/code-423n4/2022-06-illuminate/blob/912be2a90ded4a557f121fe565d12ec48d0c4684/lender/Lender.sol#L145
https://github.com/code-423n4/2022-06-illuminate/blob/912be2a90ded4a557f121fe565d12ec48d0c4684/lender/Lender.sol#L156
https://github.com/code-423n4/2022-06-illuminate/blob/912be2a90ded4a557f121fe565d12ec48d0c4684/lender/Lender.sol#L708


# Vulnerability details

## Impact

There are numerous methods that the admin could apply to rug pull the protocol and take all user funds.

- `Lender.approve()`
  - Both the functions on lines #78 and #107.
  - Admin can approve any token for an arbitrary address and transfer tokens out.

- `Lender.setFee()`
  - Does not have an lower limit. 
   - `feeNominator = 1` implies 100% of amount is taken as fees.

- `Lender.withdraw()`
  - Allows withdrawing any arbitrary ERC20 token
  - 3 Days is insufficient time for users to withdraw funds in the case of a rugpull.

- `MarketPlace.setPrincipal()`
  - Use (u, m, 0) -> to be an existing Illuminate PT from another market
  - Then set (u, m, 1) -> to be some malcious admin created ERC20 token to which they have infinite supply
  - Then call `Lender.mint()` for `(u, m, 1) and later redeem these tokens on the original market

## Recommended Mitigation Steps

Without significant redesign it is not possible to avoid the admin being able to rug pull the protocol.

As a result the recommendation is to set all admin functions behind either a timelocked DAO or at least a timelocked multisig contract.
