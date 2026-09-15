# [H] SushiSwap incident: SUSHI RouteProcessor2 was attacked and lost about 1800 ETH, about $3.34 million. According to the analysis of SlowMist, the root c

## Summary
Severity: High
Target: SushiSwap
Loss: $ 3,340,000
Attack method: Unchecked Input Data
Published: 2023-04-09
Source: https://twitter.com/SlowMist_Team/status/1644936375924584449
Type: slowmist-incident

## Details
SUSHI RouteProcessor2 was attacked and lost about 1800 ETH, about $3.34 million. According to the analysis of SlowMist, the root cause is that ProcessRoute does not perform any checks on the route parameters passed in by the user, which leads the attacker to use this problem to construct a malicious route parameter so that the Pool read by the contract is created by the attacker. On April 19, SushiSwap released a postmortem analysis report stating that due to 18 replayed transactions, the 1,800 WETH initially depleted from the first user’s wallet ended up in multiple wallets. A total of 885 ETH have been refunded so far. Of these, approximately 685 ETH were sent to Sushi core contributors to operate the multisig, 190 ETH were sent to affected users, and 10 ETH were sent to the Sushi rescue contract.
