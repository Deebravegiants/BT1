# [C] Fei Protocol & Rari Capital incident: Fei Protocol officially tweeted that it has noticed multiple exploits of Rari Capital’s Fuse pool, has identified the root cause a

## Summary
Severity: Critical
Target: Fei Protocol & Rari Capital
Loss: $ 80,000,000
Attack method: Reentrancy Attack
Published: 2022-04-30
Source: https://twitter.com/feiprotocol/status/1520344430242254849
Type: slowmist-incident

## Details
Fei Protocol officially tweeted that it has noticed multiple exploits of Rari Capital’s Fuse pool, has identified the root cause and suspended all lending to mitigate further losses. And shout that hackers, if they can return user funds, will get a bounty of 10 million US dollars. According to previous news, Fei Protocol was attacked, and the loss exceeded 28,380 ETH, about 80.34 million US dollars. The attacker's address was 0x6162759eDAd730152F0dF8115c698a42E666157F. The Rari Capital pool was attacked due to a classic reentrancy vulnerability. Its function exitMaket has no reentrancy protection.
