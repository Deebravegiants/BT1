# [M] Revest Finance incident: DeFi protocol Revest Finance has been hacked. Hackers stole nearly 7.7 million ECO, 579 LYXe, nearly 715 million BLOCKS, and over

## Summary
Severity: Medium
Target: Revest Finance
Loss: $ 120,000
Attack method: Reentrancy Attack
Published: 2022-03-27
Source: https://twitter.com/RevestFinance/status/1507968623792607233
Type: slowmist-incident

## Details
DeFi protocol Revest Finance has been hacked. Hackers stole nearly 7.7 million ECO, 579 LYXe, nearly 715 million BLOCKS, and over 350,000 RENA. According to SlowMist analysis, this attack is because the handleMultipleDeposits function in the tokenVault contract does not determine whether the newly minted NFT exists, so the attacker uses this point to directly modify the information of the NFT that has been minted, and in the Revest contract The key functions in this are not restricted by reentrant locks, which lead to being used by callbacks.
