# [M] Mitigation Confirmed for M-05

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-05-asymmetry-mitigation
Published: 2023-05-08
Source: https://github.com/code-423n4/2023-05-asymmetry-mitigation-findings/issues/17
Type: code-finding

## Details
Note: Issue has not actually been resolved but for some reason I can't get my issues to submit without "Mitigation confirmed (no new vulnerabilities detected)" checked so I am doing this as a work around

## Severity

Medium

## Lines of code

https://github.com/asymmetryfinance/smart-contracts/pull/264/files#diff-badfabc2bc0d1b9ef5dbef737cd03dc2f570f6fd2074aea9514da9db2fff6e4eR322-R332

## Impact

## Proof of Concept

    function approxPrice() public view returns (uint256) {
        uint256 totalSupply = totalSupply();
        uint256 underlyingValue = 0;
        for (uint256 i = 0; i < derivativeCount; i++) {
            if (!settings[i].enabled) continue;
            underlyingValue +=
                (derivatives[i].ethPerDerivative() * derivatives[i].balance()) /
                10 ** 18;
        }
        if (totalSupply == 0 || underlyingValue == 0) return 10 ** 18;
        return (10 ** 18 * underlyingValue) / totalSupply;
    }

The root cause of M-05 has still not been addressed. Sponsor comment indicates they are fixing the issue that the stETH deposit limit is not accounted for. In the readme it states that this issues has been fixed by allowing derivatives to be disabled, however that doesn't address the issue at all. That's because approxPrice will exclude any derivatives that have been disabled.

Example:
Assume stETH and reth are the only derivatives and they both contain 500 of their respective asset. Now stETH reaches their deposit cap. Using the presumed solution of disabling the stETH derivative, approxPrice will now return 0.5 instead of 1. This is extremely problematic as anyone who withdraws during this period will lose half their fund and those who deposit will get double back when it is reenabled.

## Tools Used

Manual Review

## Recommended Mitigation Steps


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-05-asymmetry-mitigation-findings/issues/17_
