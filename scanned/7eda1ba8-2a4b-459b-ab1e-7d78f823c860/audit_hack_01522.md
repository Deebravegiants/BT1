# [H] Polkatrain incident: Polkatrain, an ecological IDO platform of Polkadot, had an accident this morning. According to SlowMist analysis, the contract in

## Summary
Severity: High
Target: Polkatrain
Loss: $ 3,000,000
Attack method: Arbitrage attack
Published: 2021-04-05
Source: https://polkatrain-com.gitbook.io/polkatrian-en/the-response-for-hacker-attack-incident-from-polkatrain-team
Type: slowmist-incident

## Details
Polkatrain, an ecological IDO platform of Polkadot, had an accident this morning. According to SlowMist analysis, the contract in question is the POLT_LBP contract of the Polkatrain project. This contract has a swap function and a rebate mechanism. When users purchase through the swap function When the PLOT token is used, a certain amount of rebate will be obtained, and the rebate will be forwarded to the user in the form of calling transferFrom by the _update function in the contract. Since the _update function does not set the maximum amount of rebates for a pool, nor does it determine whether the total rebates have been used up when rebates are made, malicious arbitrageurs can continuously call the swap function to exchange tokens to get the contract. Rebate reward. The SlowMist security team reminds DApp project parties to fully consider the business scenario and economic model of the project when designing the AMM exchange mechanism to prevent unexpected situations.
