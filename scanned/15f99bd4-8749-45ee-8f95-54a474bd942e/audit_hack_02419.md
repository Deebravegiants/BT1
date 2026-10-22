# [H] All vesting grants are revocable

## Summary
Severity: High
Source: https://github.com/kikinteractive/kin-token/blob/3ed3a383b9304274ec22f41769716cadb854727f/contracts/KinTokenSale.sol#L285-L286
Type: audit-issue

## Details
It should be noted that all vesting grants are [revocable](https://github.com/kikinteractive/kin-token/blob/3ed3a383b9304274ec22f41769716cadb854727f/contracts/KinTokenSale.sol#L285-L286) (indicated by the last parameter, `true`), including the large grant given to Kik. If a grant is revoked, all of its vesting tokens are immediately transferred to the owner of `VestingTrustee`. Make sure that this is in fact desired.

_**Update:** The team has clarified that this is a temporary measure so that possible errors can be fixed afterwards, and that all grants will be manually made irrevocable as soon as possible._
