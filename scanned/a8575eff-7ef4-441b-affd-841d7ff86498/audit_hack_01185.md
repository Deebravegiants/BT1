# [M] DFXFinance incident: The DFX Finance project on the ETH chain was attacked, and the attackers made a profit of about $231,138. According to SlowMist an

## Summary
Severity: Medium
Target: DFXFinance
Loss: $ 231,138
Attack method: Reentrancy Attack
Published: 2022-11-11
Source: https://www.odaily.news/newsflash/304558
Type: slowmist-incident

## Details
The DFX Finance project on the ETH chain was attacked, and the attackers made a profit of about $231,138. According to SlowMist analysis, the main reason for this attack is that the Curve contract flash loan function does not have re-entrancy protection, which causes the attack to re-enter the deposit function to transfer tokens to judge the balance of flash loan repayments. The account so that the attacker can successfully withdraw money to profit.
