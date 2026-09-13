# [H] DAO Maker incident: The Vesting contract of DAO Maker was attacked by hackers. DeRace Token (DERC), Coinspaid (CPD), Capsule Coin (CAPS), Showcase Tok

## Summary
Severity: High
Target: DAO Maker
Loss: $ 4,000,000
Attack method: Contract Vulnerability
Published: 2021-09-04
Source: https://www.coinfirm.com/blog/dao-maker-hack/
Type: slowmist-incident

## Details
The Vesting contract of DAO Maker was attacked by hackers. DeRace Token (DERC), Coinspaid (CPD), Capsule Coin (CAPS), Showcase Token (SHO) all use Dao Maker's distribution system, and the DAO Maker contract is attacked when the holder is issued (SHO) in DAO Maker , That is, there is a loophole in the distribution system of SHO participants: init is not initialized protection, the attacker initializes the key parameters of init, and changes the owner at the same time, and then steals the target token through emergencyExit and exchanges it into DAI, attacking The final profit of nearly 4 million U.S. dollars.
