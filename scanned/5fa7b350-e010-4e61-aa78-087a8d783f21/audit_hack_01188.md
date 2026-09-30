# [M] MooCakeCTX incident: The MooCakeCTX project suffered a flash loan attack, and the attackers made a profit of $143,921. According to Fairyproof’s analys

## Summary
Severity: Medium
Target: MooCakeCTX
Loss: $ 143,921
Attack method: Flash Loan Attack
Published: 2022-11-07
Source: https://www.panewslab.com/zh/sqarticledetails/vb6aozpr.html
Type: slowmist-incident

## Details
The MooCakeCTX project suffered a flash loan attack, and the attackers made a profit of $143,921. According to Fairyproof’s analysis, the suspected reason is that the contract reinvested (the earn function was not called) before the user pledged (depositAll function) without settlement of the reward, that is, when the user pledged, the contract did not settle the previous reward and conduct new investment. This will cause users to get the previous pledge dividends immediately after the pledge. After the attacker borrows 50,000 cake tokens using a flash loan in the same block, he pledges it twice in a row, and then withdraws the pledged cake tokens and returns them to make a profit.
