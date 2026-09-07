# [M] ISwivel(swivelAddr).initiate(o, a, s) return value not handled for Swivel lending in Lender.sol

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-illuminate
Published: 2022-11-10
Source: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/139
Type: sherlock-finding

## Details
ctf_sec

medium

# ISwivel(swivelAddr).initiate(o, a, s) return value not handled for Swivel lending in Lender.sol

## Summary

ISwivel(swivelAddr).initiate(o, a, s) return value not handled for Swivel lending in Lender.sol

## Vulnerability Detail

The swivel lending method is implemented below

```solidity
uint256 received;
{
// Get the starting amount of principal tokens
uint256 startingZcTokens = IERC20(
    IMarketPlace(marketPlace).token(u, m, p)
).balanceOf(address(this));

// Fill the given orders on Swivel
ISwivel(swivelAddr).initiate(o, a, s);

if (e) {
    // Calculate the premium
    uint256 premium = IERC20(u).balanceOf(address(this)) -
        starting;

    // Swap the premium for Illuminate principal tokens
    swivelLendPremium(u, m, y, premium, premiumSlippage);
}

// Compute how many principal tokens were received
received =
    IERC20(IMarketPlace(marketPlace).token(u, m, p)).balanceOf(
        address(this)
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/139_
