# [M] M-08 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-09-goodentry-mitigation
Published: 2023-09-07
Source: https://github.com/code-423n4/2023-09-goodentry-mitigation-findings/issues/3
Type: code-finding

## Details
# Lines of code

https://github.com/GoodEntry-io/ge/blob/c7c7de57902e11e66c8186d93c5bb511b53a45b8/contracts/helper/V3Proxy.sol#L160
https://github.com/GoodEntry-io/ge/blob/c7c7de57902e11e66c8186d93c5bb511b53a45b8/contracts/helper/V3Proxy.sol#L180
https://github.com/GoodEntry-io/ge/blob/c7c7de57902e11e66c8186d93c5bb511b53a45b8/contracts/helper/V3Proxy.sol#L199


# Vulnerability details

The original issue [M-08: Return value of low level call not checked](https://github.com/code-423n4/2023-08-goodentry-findings/issues/83), in scope for the mitigation review, was not acted upon, most likely overlooked during the fixing phase.




## Assessed type

call/delegatecall
