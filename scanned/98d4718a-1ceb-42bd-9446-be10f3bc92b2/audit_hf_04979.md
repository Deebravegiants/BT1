# [H] Protocol manager can steal all funds via reen-

## Summary
Severity: High
Contest weight: 0.2532
Dataset id: 22939
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Protocol manager can steal all funds via reentrancy during the 1inch swap. Protocol manager can initiate 1inch swaps via multiple Univ3 pools. The only restrictions put by the dHedge pool is that the received amount of funds should be within the set slippage %. A protocol manager can utilize this to steal all contract funds in the following way:
1. Transfer all contract funds into a single asset.
2. Initiate a 1inch swap with a custom malicious token in the middle, for almost all funds (leave a dust amount within the contract)
3. Once the funds are out of the contract and the custom token is reached, re-enter back into the contract via deposit (deposit does not have a nonReentrant modifier)
4. Since all of the funds are out of the contract, the pool's valuation will be a dust amount. Depositing a reasonable amount will result into easily getting >99.99% of the pool's token supply
5. Continue the 1inch swap and send the funds back to the pool
6. Now that the swap is concluded and funds are back in the contract, protocol manager owns almost all tokens and can withdraw everything. Protocol manager can steal all funds

## Recommendation
add nonReentrant modifier to deposit
