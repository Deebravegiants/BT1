# [M] BNO incident: BNO suffered a flash loan attack on BNBChain, resulting in a loss of about $500,000 due to business logic problems. The root cause

## Summary
Severity: Medium
Target: BNO
Loss: $ 500,000
Attack method: Flash Loan Attack
Published: 2023-07-18
Source: https://blog.solidityscan.com/bno-hack-analysis-15436d73e44e
Type: slowmist-incident

## Details
BNO suffered a flash loan attack on BNBChain, resulting in a loss of about $500,000 due to business logic problems. The root cause of the attack is a problem with the reward calculation mechanism in the pool that supports NFT and ERC20 token rights. The pool has an "emergencyWithdraw" function that allows users to withdraw their ERC20 token stake immediately. Crucially, however, this feature does not process or interpret NFT stake records. Attackers exploited this flaw by depositing NFTs and ERC20 tokens into a pool and then executing the "emergencyWithdraw" function specifically for their ERC20 tokens. By doing so, an attacker can bypass the reward calculation check, effectively manipulating the system to his advantage. Through this manipulation, an attacker is able to clear a user's "reward debt," earn undeserved rewards, and cause significant financial damage to the mining pool and its users.
