# [M] JokInTheBoxETH incident: MEV Bot JokInTheBoxETH was attacked, lost ~$34K. The root cause of the exploit was poorly implemented unstake function fo the stak

## Summary
Severity: Medium
Target: JokInTheBoxETH
Loss: $ 34,000
Attack method: Contract Vulnerability
Published: 2024-06-10
Source: https://x.com/JokInTheBoxETH/status/1800539599082500106
Type: slowmist-incident

## Details
MEV Bot JokInTheBoxETH was attacked, lost ~$34K. The root cause of the exploit was poorly implemented unstake function fo the staking contract. Since the unstake function does not check the state of the variable "unstake", the exploiter could unstake multiple times and drian the assets.
