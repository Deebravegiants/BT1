# [M] SynapLogic incident: According to a BlockSec alert, the SynapLogic contract lacked critical parameter validation in the swapExactTokensForETHSupporting

## Summary
Severity: Medium
Target: SynapLogic
Loss: $ 186,000
Attack method: Smart Contract Vulnerability
Published: 2026-01-19
Source: https://x.com/Phalcon_xyz/status/2013439544595562898
Type: slowmist-incident

## Details
According to a BlockSec alert, the SynapLogic contract lacked critical parameter validation in the swapExactTokensForETHSupportingFeeOnTransferTokens function, allowing attackers to manipulate the whitelist logic and designate arbitrary recipient addresses. In addition, the contract failed to verify whether the total amount of native tokens distributed exceeded the actual payment made, enabling attackers to withdraw excess native tokens while simultaneously receiving newly minted SYP, resulting in losses of approximately $186,000.
