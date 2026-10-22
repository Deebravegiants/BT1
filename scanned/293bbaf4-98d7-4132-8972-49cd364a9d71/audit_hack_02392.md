# [M] \[M01\] The selectedApplications array is not enforced

## Summary
Severity: Medium
Source: https://github.com/propsproject/props-token-distribution/blob/e5ce0b2df1fbe108458d86820da578db56ac28d1/contracts/token/PropsRewardsLib.sol#L42-L43
Type: audit-issue

## Details
The [currentList and previousList arrays in the selectedApplications struct](https://github.com/propsproject/props-token-distribution/blob/e5ce0b2df1fbe108458d86820da578db56ac28d1/contracts/token/PropsRewardsLib.sol#L42-L43) are controlled by the `controller` and are used to set the list of applications that are able to receive rewards. However, these arrays are never checked when rewards are being distributed. It is possible for validators to distribute rewards to applications that are not included in the `selectedApplications` arrays. Consider requiring that all applications are included in the appropriate array in the `selectedApplications` struct for a `rewardsHash` to be valid.

_Update: Fixed in [9ab4ec4](https://github.com/propsproject/props-token-distribution/commit/9ab4ec461759c4a5753f25a45d45d5c1a55c3ad2). A check was added to the `rewardsHashIsValid` function enforcing that an application is in the appropriate array in the `selectedApplications` struct._
