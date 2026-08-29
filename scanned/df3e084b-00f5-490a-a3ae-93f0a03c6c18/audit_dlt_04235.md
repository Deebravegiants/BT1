# [M] Redeemer autoRedeem will not have meaningful incentives in the case of high decimal underlyings

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-illuminate
Published: 2022-11-10
Source: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/220
Type: sherlock-finding

## Details
hyh

medium

# Redeemer autoRedeem will not have meaningful incentives in the case of high decimal underlyings

## Summary

Redeemer doesn't have the functionality to change the fee set on construction. For high decimal underlyings, for example DAI, initially set fee is just `4e-11 basis points`, which provides no incentives for third parties to run autoRedeem().

## Vulnerability Detail

`feeChange` is missing in Redeemer, which hard codes the feenominator to one set on construction, that is basically only feasible for 6 decimals underlying (`40 bp` in this case).

For all others, especially for 18 decimal ones, like DAI or LUSD, it is very close to zero and provides no incentives.

## Impact

The funds that are normally retrieved via autoRedeem will remain on the balance. Say for accounts that are unable to run redeem directly for any reason.

Setting the severity to be medium as that's an unavailability of functionality leading to temporal funds freeze.

## Code Snippet

setFee() will always revert if `feeChange` is zero:

https://github.com/sherlock-audit/2022-10-illuminate/blob/main/src/Redeemer.sol#L165-L187

```solidity
    /// @notice sets the feenominator to the given value
    /// @param f the new value of the feenominator, fees are not collected when the feenominator is 0
    /// @return bool true if successful
    function setFee(uint256 f) external authorized(admin) returns (bool) {
        uint256 feeTime = feeChange;
        if (feeTime == 0) {
            revert Exception(23, 0, 0, address(0), address(0));
        } else if (feeTime < block.timestamp) {
            revert Exception(
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/220_
