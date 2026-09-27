# [M] MAD incident: $MAD was hacked, and the hacker transferred all $MAD in the contract by directly calling the transfer function of the contract hol

## Summary
Severity: Medium
Target: MAD
Loss: $ 115,681
Attack method: Contract Vulnerability
Published: 2022-06-30
Source: https://twitter.com/BeosinAlert/status/1542517440252624896
Type: slowmist-incident

## Details
$MAD was hacked, and the hacker transferred all $MAD in the contract by directly calling the transfer function of the contract holding the token, and finally made a profit of $556 BNB (worth about $115,681), which was then transferred to Tornado.Cash. The reason is that the sensitive function was not checked in the contract that holding tokens, resulting in anyone can directly call the 0x9763a894 function to transfer out the tokens held in the contract.
