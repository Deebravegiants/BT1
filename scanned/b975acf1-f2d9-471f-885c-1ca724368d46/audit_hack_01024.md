# [C] Alchemix incident: DeFi lending protocol Alchemix said on Twitter that after receiving notification from Curve Finance that the altH/ETH pool was att

## Summary
Severity: Critical
Target: Alchemix
Loss: $ 35,315,843
Attack method: Affected by Vyper Vulnerability
Published: 2023-07-30
Source: https://twitter.com/AlchemixFi/status/1685737632133971968
Type: slowmist-incident

## Details
DeFi lending protocol Alchemix said on Twitter that after receiving notification from Curve Finance that the altH/ETH pool was attacked due to a Vyper bug, Alchemix quickly began removing AMO-controlled liquidity from the Curve pool through the AMO contract. The exploit was performed on the Curve pool contract. The Alchemix smart contract has not been compromised in any way and funds are safe. executed on the contract. Three transactions are required: unstake LP tokens from Convex, withdraw alETH from Curve pool, and withdraw ETH from Curve pool. The first transaction above has been executed, and after the second transaction is executed, 8000 ETH is removed from the Curve pool. This means that there is still about 5,000 ETH liquidity controlled by AMO in the Curve pool. In the process of removing the remaining liquidity, the alETH/ETH Curve pool was drained by the attacker. Currently, the alETH reserve has lost about 5,000 ETH. On September 4th, Alchemix issued a document stating that a white hat MEV robot operator has returned 43.3 ETH profits obtained through arbitrage from the Curve alETH/ETH pool attack incident, which will be added to the redistribution of funds.
