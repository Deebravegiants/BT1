# [M] ToBet incident: The attacker rolls back the transaction when placing a bet. From the time the bet is placed until the transaction is rolled back,

## Summary
Severity: Medium
Target: ToBet
Loss: 22,403.69 EOS
Attack method: Roll back attack
Published: 2018-12-19
Source: https://www.jinse.com/lives/71877.htm
Type: slowmist-incident

## Details
The attacker rolls back the transaction when placing a bet. From the time the bet is placed until the transaction is rolled back, the betting data will temporarily exist in the database of the current node; and Tobet queries the betting by polling the node database outside the contract. The lottery will be drawn outside the contract and the result will be passed to the lottery action; when the attacker keeps betting and rolls back the transaction, because the betting and Tobet polling use the same node, the Tobet lottery polling can query the database betting information for a short time and draw the lottery. . However, the attacker's bet was not successful, and the contract would continue to draw prizes for him, resulting in no capital arbitrage.
