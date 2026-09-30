# [M] Equilibria Finance incident: According to an announcement from Equilibria Finance, a vulnerability was discovered in the ePENDLE auto-compounder contract on Et

## Summary
Severity: Medium
Target: Equilibria Finance
Loss: $ 62,500
Attack method: Contract Vulnerability
Published: 2025-08-24
Source: https://x.com/Equilibriafi/status/1959296722930483668
Type: slowmist-incident

## Details
According to an announcement from Equilibria Finance, a vulnerability was discovered in the ePENDLE auto-compounder contract on Ethereum, resulting in a loss of approximately 13.36 ETH.

The issue stemmed from the stk-ePENDLE contract on Ethereum mainnet not being configured as non-transferable. The attacker used flash loans via Balancer to acquire ePENDLE, staked it into stk-ePENDLE, and then repeatedly transferred stk-ePENDLE across multiple addresses. Each transfer triggered a reward claim, enabling the attacker to drain the unclaimed rewards from the contract.
