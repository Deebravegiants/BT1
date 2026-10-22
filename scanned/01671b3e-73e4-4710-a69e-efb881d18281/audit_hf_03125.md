# [H] ChainlinkOracle.solgetPrice() The price will

## Summary
Severity: High
Contest weight: 0.6116
Dataset id: 17606
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
ChainlinkOracle assumes and inexplicitly requires the token's USD feed's decimals to be 8. However, there are certain tokens whose USD feed has a different number of decimals.
In the current implementation, it assumes tokenFeedDecimals = ethFeedDecimals (feed[token].decimals() must equals ethUsdPriceFeed.decimals()=8).
However, there are tokens with USD price feed's decimals != 8 (E.g: AMPL/USD).
When the token's USD feed's decimals != 8, ChainlinkOracle.solgetPrice() will return an incorrect price in ETH.
The correct calculation formula should be:
answertoken × 10ethFeedDecimals / answereth × 10tokenFeedDecimals × 1018
When the price feed with decimals!=18 is set, the attacker can deposit a small amount of the asset and drain all the funds from the protocol.

## Proof of Concept
Given:
• 1.0 AMPL worth 1.14 USD, feed[ampl].decimals()==18, answer_ampl=1140608758261546000 Source: feed[ampl]
• 1.0 ETH worth 1588.11 USD, ethUsdPriceFeed.decimals()==8, answer_eth=158811562094 Source: ethUsdPriceFeed
chainlinkOracle.getPrice(AMPL) will return ~7.18m (eth):
answertoken × 1018 / answereth = 1140608758261546000 × 1018 / 158811562094 = 7182151873718260663354494

## Recommendation
Consider adding a check for feed.decimals() to make sure feed's decimals = 8:
```solidity
constructor(AggregatorV3Interface _ethUsdPriceFeed) Ownable(msg.sender) {
    require(_ethUsdPriceFeed.decimals() == 8, "...");
    ethUsdPriceFeed = _ethUsdPriceFeed;
}

function setFeed(
    address token,
    AggregatorV3Interface _feed
) external adminOnly {
    require(_feed.decimals() == 8, "...");
    feed[token] = _feed;
    emit UpdateFeed(token, address(_feed));
}
```
Our chainlink oracles use token/usd feed for all the assets we support via chainlink, all the token/usd chainlink feeds have 8 decimals and hence will not lead to any issue.
Confirmed fix.
