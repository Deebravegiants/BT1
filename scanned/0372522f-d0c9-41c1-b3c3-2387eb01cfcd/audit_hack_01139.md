# [M] Hedera incident: Hedera tweeted to disclose the details of the attack. The attacker attacked the smart contract service code of the Hedera main net

## Summary
Severity: Medium
Target: Hedera
Loss: $ 570,000
Attack method: Contract Vulnerability
Published: 2023-03-10
Source: https://twitter.com/hedera/status/1634055353435561986
Type: slowmist-incident

## Details
Hedera tweeted to disclose the details of the attack. The attacker attacked the smart contract service code of the Hedera main network and transferred the Hedera Token Service tokens held by some user accounts to their own accounts. The attackers targeted accounts used as liquidity pools on multiple DEXs migrated to use the Hedera Token Service using Uniswap V2-derived contract generations, including Pangolin Hedera, SaucerSwap, and HeliSwap. When attackers moved tokens obtained through the attack to a Hashport Network bridge, bridge operators detected the activity and acted quickly to disable it. To prevent attackers from stealing more tokens, Hedera shut down the mainnet proxy, which removes user access to the mainnet.
