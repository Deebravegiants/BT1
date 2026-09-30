# [C] GLOBAL-1 | Orders Requiring More Than 5 Million Gas Cannot Execute

## Summary
Severity: Critical
Contest weight: 0.2207
Dataset id: 19260
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Chainlink automation keepers are configured to send 5,000,000 gas with each execution, however GMX deposits, withdrawals, and orders may often require more than 5,000,000 gas to execute. In the [general.ts](https://github.com/gmx-io/gmx-synthetics/blob/a0c652ad9691d1db369c238331e3170f442e7ae1/config/general.ts#L61) configuration file the increaseOrderGasLimit and decreaseOrderGasLimit are configured to 4_000_000, additionally the minAdditionalGasForExecution is configured to 1_000_000. Therefore any increase or decrease order including a callback with a nonzero callbackGasLimit cannot be executed by the Chainlink automation keepers. Additionally the singleSwapGasLimit is configured to 1_000_000, therefore deposits and withdrawals with 4 or more total swaps in the longTokenSwapPath and shortTokenSwapPath are unable to be executed by the Chainlink automation keepers.

## Recommendation
Increase the configured gas amount to as high as 15,000,000 to ensure that even the most expensive of actions can be executed on GMX V2.
