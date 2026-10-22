# [M] Cashback on referral

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-02-aave-lens
Published: 2022-02-14
Source: https://github.com/code-423n4/2022-02-aave-lens-findings/issues/20
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-02-aave-lens/blob/aaf6c116345f3647e11a35010f28e3b90e7b4862/contracts/core/modules/collect/FeeCollectModule.sol#L99


# Vulnerability details

## Impact
In the fee collect modules like `FeeCollectModule` there is no prevention of someone submitting a second profile they own as the `referrerProfileId` in `processCollect` to receive back part of the fees paid.

The referral system is essentially broken as all rational agents will submit a second profile they control to get back part of the fees.
One could even create a referrer smart contract profile that anyone can submit which automatically refunds the fee received.
A [similar royalties/referral fees issue](https://github.com/code-423n4/2021-11-nested-findings/issues/30) was judged high-severity recently.

## Recommended Mitigation Steps
There's no way to avoid this except by not allowing any profile as a referrer.
Whitelist certain important infrastructure providers, like different frontends, as referrers and only allow these to be used instead of users submitting their alt profiles.
