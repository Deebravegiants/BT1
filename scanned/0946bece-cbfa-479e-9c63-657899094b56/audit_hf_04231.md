# [M] M-09 | Risk Free Trade With Merge Callbacks

## Summary
Severity: Medium
Contest weight: 0.2123
Dataset id: 21127
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
PoC Order execution with the settleOrder function requires that the priceUpdateData provided to parse the pythPrice is for the price update that satisfies the minimum and maximum times (commitmentTime + 12 seconds, commitmentTime + 60 seconds) as well as that the publish time of the price update that is sequentially previous to the provided price data took place before the minimum commitmentTime. Therefore only prices that satisfy these constraints may be used to execute an order while it is ready and not stale. A malicious user may prevent an order from being executable in the block where the valid price data is accurate and only allow the order to go through once a significant period of time has passed and the user observes that the true current price of the index asset has moved in their favor. The order will only be executable with the outdated price, and therefore the user will realize a risk-free profit based upon how much price has diverged in the user’s favor since then. The malicious user may prevent their order from being executable by registering a mergeAccounts hook as a callback where the user’s position as the fromAccount has sUSD collateral in addition to the market’s index as collateral and therefore reverts. When the malicious user wishes their order to be executable, e.g. they have determined that price has moved in a direction that is favorable to them, they may remove the sUSD collateral with the payDebt function, assuming they have a pre-existing position with debt, and execute their order with the outdated price.

## Recommendation
Consider increasing the orderFee percentage that is taken to dissuade from any risk-free short term trades. Otherwise consider removing the possibility for users to control whether or not their orders are executable by way of callbacks through a try/catch wrapper.
