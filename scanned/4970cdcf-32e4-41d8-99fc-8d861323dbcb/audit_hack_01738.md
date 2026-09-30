# [M] FFgame incident: By deploying the attack contract and using the same algorithm as FFgame to calculate the random number in the contract, the attack

## Summary
Severity: Medium
Target: FFgame
Loss: 1,331 EOS
Attack method: Random number attack
Published: 2018-11-08
Source: https://www.jinse.com/lives/62867.htm
Type: slowmist-incident

## Details
By deploying the attack contract and using the same algorithm as FFgame to calculate the random number in the contract, the attacker immediately uses the random number attack contract in inline_action after generating the random number, resulting in the winning result being "predicted", thus reaching the super high winning rate.
