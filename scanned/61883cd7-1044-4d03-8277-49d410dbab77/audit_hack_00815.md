# [H] Velocore incident: DEX Velocore experienced a security breach on June 2nd, 2024, resulting in financial losses approximating $6.8 million in ETH. The

## Summary
Severity: High
Target: Velocore
Loss: $ 6,800,000
Attack method: Contract Vulnerability
Published: 2024-06-02
Source: https://velocorexyz.medium.com/velocore-incident-post-mortem-6197020ec3e9
Type: slowmist-incident

## Details
DEX Velocore experienced a security breach on June 2nd, 2024, resulting in financial losses approximating $6.8 million in ETH. The primary cause of the incident was faulty logic within the velocore__execute() function of the ConstantProductPool. When a user makes a swap on Velocore, the Vault contract makes an external call to this function to calculate the result of the swap.
