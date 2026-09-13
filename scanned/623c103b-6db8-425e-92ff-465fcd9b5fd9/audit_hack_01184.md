# [M] SheepFarm incident: The SheepFarm project on the BNB chain was attacked by a vulnerability. After analysis, it was found that because the register fun

## Summary
Severity: Medium
Target: SheepFarm
Loss: 262 BNB
Attack method: Contract Vulnerability
Published: 2022-11-16
Source: https://www.panewslab.com/zh/sqarticledetails/nmuct2g5.html
Type: slowmist-incident

## Details
The SheepFarm project on the BNB chain was attacked by a vulnerability. After analysis, it was found that because the register function of the SheepFarm contract could be called multiple times, the attacker 0x2131c67ed7b6aa01b7aa308c71991ef5baedd049 used the register function multiple times to increase his own gems, and then used the upgradeVillage function to accumulate yield while consuming gems properties, and finally call the sellVillage method to convert yield to money before withdrawing money. The attack caused the project to lose about 262 BNB, about $72,000.
