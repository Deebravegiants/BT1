# [C] Pickle Finance incident: Ethereum DeFi project Pickle Finance was attacked, losing about 20 million DAI. According to SlowMist analysis, the attacker compl

## Summary
Severity: Critical
Target: Pickle Finance
Loss: $ 20,000,000
Attack method: Fake currency for real currency
Published: 2020-11-22
Source: https://twitter.com/picklefinance/status/1330242051468910596
Type: slowmist-incident

## Details
Ethereum DeFi project Pickle Finance was attacked, losing about 20 million DAI. According to SlowMist analysis, the attacker completes an attack by forging the contract addresses of _fromJar and _toJar when calling the swapExactJarForJar function in the Controller contract, and then transferring the fake currency in exchange for the real DAI in the contract. SlowMist indicates that the swapExactJarForJar function in Pickle Finance's Controller contract allows two arbitrary jar contract addresses to be passed in for token exchange. Among them, _fromJar, _toJar, _fromJarAmount, and _toJarMinAmount are all variables that users can control. Attackers use this feature, fill in both _fromJar and _toJar with their own addresses, and _fromJarAmount is the amount of DAI set by the attacker to extract the contract, about 20 million DAI.
