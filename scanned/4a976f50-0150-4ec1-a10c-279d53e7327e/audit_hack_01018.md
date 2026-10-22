# [M] Earning.Farm incident: The DeFi project Earning.Farm suffered a reentrancy attack and lost 286 ETH (approximately $530,000). According to the analysis of

## Summary
Severity: Medium
Target: Earning.Farm
Loss: $ 530,000
Attack method: Reentrancy Attack
Published: 2023-08-09
Source: https://etherscan.io/address/0xee4b3dd20902Fa3539706F25005fa51D3b7bDF1b
Type: slowmist-incident

## Details
The DeFi project Earning.Farm suffered a reentrancy attack and lost 286 ETH (approximately $530,000). According to the analysis of SlowMist, the attacker re-enters the transfer function of LP to transfer LP tokens when withdrawing money, making the balance of the account smaller than the previously calculated shares value, triggering the logic of updating the shares value, resulting in the number of manipulated LPs being updated to the desired value. In terms of the value of the burned shares, this resulted in the final amount of LP burned being much smaller than expected, and the user can withdraw the funds in the pool by withdrawing the transferred LP again.
