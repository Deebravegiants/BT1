# [H] EvoDefi incident: EvoDefi, the project revenue farm on the BSC chain, was attacked, and the price of its token GEN dropped from US$2.1/piece to US$0

## Summary
Severity: High
Target: EvoDefi
Loss: $ 1,000,000
Attack method: Flash loan attack
Published: 2021-06-10
Source: https://medium.com/@Knownsec_Blockchain_Lab/knownsec-blockchain-lab-evodefi-attack-event-analysis-e1cba8a789ce
Type: slowmist-incident

## Details
EvoDefi, the project revenue farm on the BSC chain, was attacked, and the price of its token GEN dropped from US$2.1/piece to US$0.9/piece, a short-term drop of 57%. Loss of 455,576.85 GEN worth approximately USD 1 million. Due to the design flaws in the update logic of the function in the MasterChef contract, the part of the reward that needs to be deducted is not updated, which leads to arbitrage by the attacker.
