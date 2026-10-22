# [M] Amount of tier winners can not be reduced in payoutSchedule

## Summary
Severity: Medium
Reporter: minhtrng
Source: https://github.com/sherlock-audit/2023-02-openq/blob/fc2dae7107e4be0878ace40b1e7218c18e1933fe/contracts/Bounty/Implementations/TieredFixedBountyV1.sol#L151-L170
Type: audit-issue

## Details
# Amount of tier winners can not be reduced in payoutSchedule

## Summary

Attempting to decrease the length of the payoutScedule will revert, which will make it impossible to adjust payouts in case there are less tier winners than anticipated.

## Vulnerability Detail

The functions `TieredPercentageBountyV1.setPayoutSchedule` and `TieredFixedBountyV1.setPayoutScheduleFixed` can be used to adjust the payoutSchedule for the tier winners. This should include changing the amount of tier winners. However, in the current implementation it is not possible to lower the amount of tiers, due to incorrect iteration logic:

```js
string[] memory newTierWinners = new string[](payoutSchedule.length);
bool[] memory newInvoiceComplete = new bool[](payoutSchedule.length);
bool[] memory newSupportingDocumentsCompleted = new bool[](
    payoutSchedule.length
);

for (uint256 i = 0; i < tierWinners.length; i++) {
    newTierWinners[i] = tierWinners[i];
}
tierWinners = newTierWinners;

// same iteration logic for invoiceComplete and supportingDocumentsComplete
// ...
```

Assume the initial payoutSchedule used in `initialize` contained 3 elements (meaning bounty has 3 tier winners for its contest) then `tierWinners.length` will also be 3. Now, further assume that there is a contest where only 2 submissions where valid or had high enough quality to be accepted. From a business-level perspective it makes sense for the bounty issuer to redistribute the payouts from the 3rd tier to the 1st and 2nd place.

The fact that it should be possible to lower the payout schedule size is also evidenced by this comment in the code:

```js
 // NOTE: If resizing to fewer tiers than previously, the final indexes will be removed
```

Due to the logic of resizing used above however, the call to readjust the payouts will revert if `payout.schedule < tierWinners.length`, due to trying to access an array element which is out-of-bounds. This has been tested in this [Gist](https://gist.github.com/Minh-Trng/8ed78c52154f1170b2b6ec956349f838) (copy of `TieredFixedBounty.test.js` with the additional test `'setting payout schedule with less elements'`)

## Impact

The payouts of tiers that are not occupied by anyone can not be redistributed to tiers where a winner is set (loss of rewards)

## Code Snippet

https://github.com/sherlock-audit/2023-02-openq/blob/fc2dae7107e4be0878ace40b1e7218c18e1933fe/contracts/Bounty/Implementations/TieredFixedBountyV1.sol#L151-L170

https://github.com/sherlock-audit/2023-02-openq/blob/fc2dae7107e4be0878ace40b1e7218c18e1933fe/contracts/Bounty/Implementations/TieredPercentageBountyV1.sol#L159-L178

## Tool used

Manual Review

## Recommendation

In the loops that are used to resize the metadata arrays (`tierWinners`, `invoiceComplete`, `supportingDocumentsComplete`), iterate over `min(payoutSchedule.length, metadataArray.length)`
