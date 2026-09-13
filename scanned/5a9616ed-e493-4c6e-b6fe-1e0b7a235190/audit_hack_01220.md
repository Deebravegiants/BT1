# [M] BXH incident: The TokenStakingPoolDelegate contract updated by BXH after the last attack suffered another flash loan attack. The contract lost 4

## Summary
Severity: Medium
Target: BXH
Loss: 40,085 USDT
Attack method: Flash Loan Attack
Published: 2022-09-28
Source: https://www.odaily.news/newsflash/300625
Type: slowmist-incident

## Details
The TokenStakingPoolDelegate contract updated by BXH after the last attack suffered another flash loan attack. The contract lost 40,085 USDT, and the attacker made a profit of 31,794 USDT after paying off the flash loan fee. After analysis, this attack is caused by the use of getReserves() in the contract's getITokenBonusAmount function to obtain the instantaneous quotation, so that the attacker can make a profit by manipulating the quotation.
