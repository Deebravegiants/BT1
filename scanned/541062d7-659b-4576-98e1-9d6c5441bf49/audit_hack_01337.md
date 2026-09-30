# [H] Agave incident: The Agave contract on Gnosis Chain was attacked due to an untrusted external call. The attacker calls the liquidateCall function t

## Summary
Severity: High
Target: Agave
Loss: $ 5,400,000
Attack method: Flash loan attack
Published: 2022-03-15
Source: https://twitter.com/Agave_lending/status/1503725275917565954
Type: slowmist-incident

## Details
The Agave contract on Gnosis Chain was attacked due to an untrusted external call. The attacker calls the liquidateCall function to liquidate himself without any debt. During the liquidation process, the liquidation contract called the attacker contract. During the process, the attack contract deposited 2728 WETH obtained through the flash loan and minted 2728 aWETH. And use this as collateral to lend out all available assets in the Agave project. After the external call ends, the liquidateCall function directly liquidates the 2728 aWETH previously deposited by the attacker and transfers it to the liquidator.
