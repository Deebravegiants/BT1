# [H] Inaccurate Gas Estimations In mint()

## Summary
Severity: High
Contest weight: 0.2468
Dataset id: 15135
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During the execution of mint() the execution costs are estimated in txCost, at the end of execution this cost is then subtracted from the receiver of the mint and given to the refundAddress. Which incentives relayers to call mint() in the name of minters, who may not have funds yet to pay for execution costs themselves. However, the calculations for the txCost are inaccurate.
Several gas costs are unaccounted for such as execution of the function selector, ABI decoding and potential memory expansion for emitting the event. Additionally, the call on line [80] is assumed to use 2300 gas, however a value transfer to a cold and empty account will cost at least 34300 gas. Furthermore, if the destination address is a smart contract its execution cost may be arbitrarily large as it executes bytecode.
As such, the destination may spend an arbitrary amount of gas during the call. This gas cost would not be subtracted from the amount minted to the user and the relayer would absorb the fees.

## Recommendation
It is recommended to update the gas cost estimations to be more accurate by using testing tools such as Forge. Additionally, consider limiting the gas stipend for the call to destination on line [80] to limit 'gas stealing' attacks.
