# [M] wstETHChainlinkOracle.sol#L26-L44 : valid time check is missed while getting the price feed data.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-notional
Published: 2022-10-13
Source: https://github.com/sherlock-audit/2022-09-notional-judging/issues/138
Type: sherlock-finding

## Details
ak1

high

# wstETHChainlinkOracle.sol#L26-L44 : valid time check is missed while getting the price feed data.

## Summary
wstETHChainlinkOracle.sol#L26-L44 : valid time check is missed while getting the price feed data.

## Vulnerability Detail
        int256 baseAnswer;
        (
            roundId,
            baseAnswer,
            startedAt,
            updatedAt,
            answeredInRound
        ) = baseOracle.latestRoundData();
        require(baseAnswer > 0, "Chainlink Rate Error");


        answer = baseAnswer * wstETH.stEthPerToken().toInt() / baseDecimals;

`updatedAt` could be zero. If it zero, price calculation should not be allowed.

## Impact
The data obtained could be invalid but not the latest.

## Code Snippet
https://github.com/sherlock-audit/2022-09-notional/blob/main/leveraged-vaults/contracts/trading/oracles/wstETHChainlinkOracle.sol#L33-L43
## Tool used
Manual Review

## Recommendation
Check for time whether it is zero.
if it zero, revert the price calculation.
Add the below check before calculating the `answer`
`require(updatedAt != 0, "updatedAt== 0 !");`

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-notional-judging/issues/138_
