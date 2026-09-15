# [M] Earning.Farm incident: The EFLeverVault contract of Earning.Farm was attacked twice by flash loans. The first attack was intercepted by MEV bot, causing

## Summary
Severity: Medium
Target: Earning.Farm
Loss: 268 ETH
Attack method: Flash Loan Attack
Published: 2022-10-15
Source: https://twitter.com/SupremacyHQ/status/1581012823701786624
Type: slowmist-incident

## Details
The EFLeverVault contract of Earning.Farm was attacked twice by flash loans. The first attack was intercepted by MEV bot, causing the contract to lose 480 ETH; the second hacker completed the attack, and the hacker made a profit of 268 ETH. After analysis, the vulnerability is caused by the contract’s flash loan callback function not verifying the flash loan initiator. The attacker can trigger the contract’s flash loan callback logic by itself: repay the Aave stETH debt in the contract and withdraw cash, and then exchange stETH for ETH. Then the attacker can call the withdraw function to withdraw the ETH balance in all contracts.
