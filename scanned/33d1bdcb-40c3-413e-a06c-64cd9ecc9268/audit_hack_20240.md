# [M] 5.2.13FeeCollectornot well integrated

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** FeeCollector.sol
**Description:** There is a contract to pay fees for using the bridge: FeeCollector. This is used by crafting a
transaction by the frontend API, which then calls the contract via_executeAndCheckSwaps().
Here is an example of the contract Here is an example of the contract of such a transaction Its whitelisted here
This way no fees are paid if a developer is using the LiFi contracts directly. Also it is using a mechanism that isn’t
suited for this. The_executeAndCheckSwaps()is geared for swaps and has several checks on balances. These
(and future) checks could interfere with the fee payments. Also this is a complicated and non transparent approach.
The project has suggested to see_executeAndCheckSwaps()as amulticallmechanism.
**Recommendation:** Use a dedicated mechanism to pay for fees.
If_executeAndCheckSwaps()is intended to be amulticallmechanism then rename the function.
**LiFi:** We acknowledge the risk and encourage integrators to utilize our API at this time.
**Spearbit:** Acknowledged.
