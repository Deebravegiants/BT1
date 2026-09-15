# [C] Kyber Network incident: Kyber Network tweeted that KyberSwap Elastic has experienced a security incident. According to the analysis of the SlowMist securi

## Summary
Severity: Critical
Target: Kyber Network
Loss: $ 54,700,000
Attack method: Liquidity Exploit
Published: 2023-11-23
Source: https://twitter.com/KyberNetwork/status/1727475235342217682
Type: slowmist-incident

## Details
Kyber Network tweeted that KyberSwap Elastic has experienced a security incident. According to the analysis of the SlowMist security team, the root cause of this attack is that in calculating the number of tokens needed for the exchange from the current price to the boundary scale price, the liquidity will be added to the portion of the fee compounding because of KyberSwap Elastic's reinvestment curve, thus causing its calculation result to be larger than expected, which can cover the user's need for exchange, but the actual price has already crossed the boundary scale, which makes the protocol think that the liquidity within the current scale has already met the need for exchange, and therefore does not carry out liquidity update. The protocol assumes that the liquidity within the current scale is sufficient to cover the redemption needs, and therefore does not update the liquidity. The result is that the liquidity is increased twice when the reverse exchange crosses the boundary scale, allowing the attacker to obtain more tokens than expected. On Nov. 27, the Kyber Network tweeted that the KyberSwap team had contacted the owner of the frontrun bots that had withdrawn approximately $5.7 million from the KyberSwap pool on Polygon and Avalanche. After negotiations, the owners of the frontrun bots have agreed to return 90% of their users' funds to a designated address. In return, they will receive a 10% bounty. On December 13th, the KyberSwap team recovered approximately $508,000 worth of funds from the owners of frontrun bots. To date, the total amount of funds returned by the owners of frontrun bots is approximately $5.17 million.
