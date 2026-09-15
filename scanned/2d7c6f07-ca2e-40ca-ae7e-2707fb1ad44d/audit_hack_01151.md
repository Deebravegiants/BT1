# [H] dForce incident: The DeFi aggregation platform dForce was attacked in Arbitrum and Optimism, and the attackers made a profit of about 3.65 million

## Summary
Severity: High
Target: dForce
Loss: $ 3,650,000
Attack method: Price Manipulation
Published: 2023-02-10
Source: https://twitter.com/dForcenet/status/1623904209161830401
Type: slowmist-incident

## Details
The DeFi aggregation platform dForce was attacked in Arbitrum and Optimism, and the attackers made a profit of about 3.65 million US dollars. According to the analysis of SlowMist, the root cause of this attack is that the attacker used the process of first transferring Native tokens and then burning LP when removing liquidity in wstETH/ETH Pool, triggering the callback of receiving Native tokens to re-enter to manipulate the virtual price and Liquidate other users for profit. On February 13, dForce tweeted that the attackers had returned all stolen funds to the project multi-signature addresses on Arbitrum and Optimism, and all affected users would be compensated.
