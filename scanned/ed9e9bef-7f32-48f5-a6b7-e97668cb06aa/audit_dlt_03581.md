# [H] Claiming prizes will be bricked if prize periods are not aligned with twab periods

## Summary
Severity: High
Chain: Smart contract
Component: 2023-08-pooltogether-mitigation
Published: 2023-08-26
Source: https://github.com/code-423n4/2023-08-pooltogether-mitigation-findings/issues/99
Type: code-finding

## Details
# Lines of code

https://github.com/GenerationSoftware/pt-v5-twab-controller/blob/main/src/TwabController.sol#L281-L299
https://github.com/GenerationSoftware/pt-v5-twab-controller/blob/main/src/libraries/TwabLib.sol#L244-L251
https://github.com/GenerationSoftware/pt-v5-twab-controller/blob/main/src/libraries/TwabLib.sol#L650-L658


# Vulnerability details

## Comments
The previous implementation allowed a malicious user to keep updating their balances provided the previous observation fell within the same period. As such, if a draw ends part way through a period, the user would be able to manipulate their average balance for period and therefore increase their odds of winning in that draw despite the draw already being closed.

Note: I have arbitrarily chosen M-13 for this report rather than M-03 since both share the same PR for their respective mitigations.

## Mitigation
The updated implementation overlaps with M-03 and ensures that twab queries are aligned on twab period boundaries. It also ensures that any Twab queries have an end time that is finalised; i.e. the period that is being queried for has ended. This ensures that a user can't manipulate their Twab balance between the time that a draw period ends and a Twab period ends. The original issue has been resolved, but a new issue has been introduced.

## New issue
Claiming prizes is bricked if prize periods are not aligned with twab periods

## Proof Of Concept
Although the updated logic solves the original issue about ensuring that the observations are safe (i.e. finalised) and observations can't be manipulated, the change has introduced a new issue where prize claiming is bricked if the twab periods are not completely aligned or are not significantly shorter than the prize pool periods (claiming is still bricked, but for a shorter duration). This was not the case before and in fact the only requirement was that “It is imperative that PoolTogether uses periods that are smaller than a single draw”. With the change, this is now only partially true. Either the Twab period needs to be significantly smaller than a prize draw period, or alternatively the period needs to be exactly aligned with the draw period. For example, if a draw is 1 day but the period for the accumulator is 20 hours it is possible that the there will be a 20 hour period during which any claims will revert due to the end time not yet being finalised. This could result in two possible issues: either prizes will go unclaimed altogether, or more fees are paid to claimers since the price of the auction is increasing during this bricked period. Claiming prizes will be bricked up to the maximum period length of the accumulator, assuming the twab period started 1 second before the draw period ended and the twab period was the same length as the draw period.

To illustrate this issue further, let's explore the updated implementation. When prizes are claimed, the winning odds are calculated, which includes a call to `getTwabBetween` in the `TwabController.sol` contract:

```
  function getTwabBetween(
    address vault,
    address user,
    uint32 startTime,
    uint32 endTime
  ) external view returns (uint256) {
    TwabLib.Account storage _account = userObservations[vault][user];
    // We snap the timestamps to the period end on or after the timestamp because the total supply records will be sparsely populated.
    // if two users update during a period, then the total supply observation will only exist for the last one.
    return
      TwabLib.getTwabBetween(
        PERIOD_LENGTH,
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-08-pooltogether-mitigation-findings/issues/99_
