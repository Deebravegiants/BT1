# [C] Harvest Finance incident: Data on the chain shows that a large amount of funds in the Harvest Finance fund pool were transferred, and about 24 million US do

## Summary
Severity: Critical
Target: Harvest Finance
Loss: $ 21,500,000
Attack method: Flash loan attack
Published: 2020-10-26
Source: https://www.zdnet.com/article/hacker-steals-24-million-from-cryptocurrency-service-harvest-finance/
Type: slowmist-incident

## Details
Data on the chain shows that a large amount of funds in the Harvest Finance fund pool were transferred, and about 24 million US dollars （Specifically, approximately USD 34 million）were successfully cashed out through multiple contract transactions, most of which were cashed out through renBTC. The initial ETH source used by the hacker this time was the Ethereum anonymous transfer platform Tornado.cash. The Hash for this operation is: 0x35f8d2f572fceaac9288e5d462117850ef2694786992a8c3f6d02612277b0877. It can be seen from the Ethereum browser that the hacker transferred 20 WETH to the Harvest Finance contract (address: 0xc6028a9fa486f52efd2b95b949ac630d287ce0af), and finally transferred the 20 ETH back to his address. Harvest Finance updated its Twitter saying that, like other arbitrage economic attacks, this time it originated from a huge flash loan and manipulated the price of one currency Lego (Curve y Pool) many times to deplete another currency Lego (fUSDT, fUSDC) Of funds. The attacker then converted the funds into renBTC and cashed out. Like other lightning loan attacks, the attacker did not give a response time, and attacked end-to-end for 7 minutes. The attacker returned $2,478,549.94 to Deployer in the form of USDT and USDC. On December 7, Harvest Finance officially announced the launch of GRAIN, USDC and USDT claim portals. Officials said that according to the previous hacker's refund of $2.5 million in funds, this reduced user losses to 13.5%. Officials are using USDC, USDT, and GRAIN tokens for mixed compensation to help users who were previously affected by the attack to make claims. Users will receive GRAIN tokens in proportion to their deposits, and the $2.5 million returned by hackers will be distributed proportionally.
