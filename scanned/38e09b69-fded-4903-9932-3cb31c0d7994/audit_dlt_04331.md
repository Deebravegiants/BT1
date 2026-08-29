# [M] Stream.balanceOf for payer doesn't consider extra tokens sent to contract

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-nounsdao
Published: 2022-12-07
Source: https://github.com/sherlock-audit/2022-11-nounsdao-judging/issues/13
Type: sherlock-finding

## Details
rvierdiiev

medium

# Stream.balanceOf for payer doesn't consider extra tokens sent to contract

## Summary
Stream.balanceOf for payer doesn't consider extra tokens sent to contract. As result it shows less balance of payer when contract contains more payment tokens than tokenAmount().
## Vulnerability Detail
https://github.com/sherlock-audit/2022-11-nounsdao/blob/main/src/Stream.sol#L285-L297
```solidity
    function balanceOf(address who) public view returns (uint256) {
        uint256 recipientBalance = _recipientBalance();


        if (who == recipient()) return recipientBalance;
        if (who == payer()) {
            // This is safe because it should always be the case that:
            // remainingBalance >= recipientBalance.
            unchecked {
                return remainingBalance - recipientBalance;
            }
        }
        return 0;
    }
```
When Stream.balanceOf calculates balance of payer it doesn't take into account extra tokens that are controlled by contract.
It calculate balance as remainingTokens - recipientBalance.

However it's possible that payer toped up Stream with more tokens than tokenAmount(). In such case those tokens should be also included in payer balance.

Scenario
1.Stream for 100$ created.
2.Payer toped up Stream with 101$.
3.On block.timestamp < startTime function Stream.balanceOf(payer) shows 100$, but should show 101$.
## Impact
Incorrect amount provided. Payer will see less funds that he has.
## Code Snippet

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-nounsdao-judging/issues/13_
