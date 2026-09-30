# [H] Maverick oracle can be manipulated

## Summary
Severity: High
Contest weight: 0.2880
Dataset id: 20286
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the MavEthOracle contract, getPriceInEth function utilizes the reserves of the Maverick pool and multiplies them with the external prices of the tokens (obtained from the rootPriceOracle contract) to calculate the total value of the Maverick position.
However, the reserves of a Maverick position can fluctuate when the price of the Maverick pool changes. Therefore, the returned price of this function can be manipulated by swapping a significant amount of tokens into the Maverick pool. An attacker can utilize a flash loan to initiate a swap, thereby changing the price either upwards or downwards, and subsequently swapping back to repay the flash loan.
Attacker can decrease the returned price of MavEthOracle by swapping a large amount of the higher value token for the lower value token, and vice versa.
Here is a test file that demonstrates how the price of the MavEthOracle contract can be manipulated by swapping to change the reserves.
There are multiple impacts that an attacker can exploit by manipulating the price of MavEthOracle:
• Decreasing the oracle price to lower the totalDebt of LMPVault, in order to receive more LMPVault shares.
• Increasing the oracle price to raise the totalDebt of LMPVault, in order to receive more withdrawn tokens.
• Manipulating the results of the Stats contracts to cause miscalculations for the protocol.

## Recommendation
Use another calculation for Maverick oracle
