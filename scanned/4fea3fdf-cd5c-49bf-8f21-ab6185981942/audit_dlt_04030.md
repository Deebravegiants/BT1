# [M] oracle : latestRoundData will not tell the latest price feed data.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-notional
Published: 2022-10-13
Source: https://github.com/sherlock-audit/2022-09-notional-judging/issues/136
Type: sherlock-finding

## Details
ak1

high

# oracle : latestRoundData will not tell the latest price feed data.

## Summary
The implementation that was done in `wstETHChainlinkOracle.sol` to decide the price of token will not tell the latest price feed data.
The price data could be outdated.

I see the price feed data is used in other contracts as well.

## Vulnerability Detail
old price feed data can be used to decide the price of the token.
Either the price could be low or high. but it is not the latest data.

    function _calculateAnswer() internal view returns (
        uint80 roundId,
        int256 answer,
        uint256 startedAt,
        uint256 updatedAt,
        uint80 answeredInRound
    ) {
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
    }

when we look at the price calculation, the data obtained could be `answeredInRound < roundId` which means that the data could be older one.

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-notional-judging/issues/136_
