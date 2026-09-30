# [M] GLOBAL-1 | Centralization Risk

## Summary
Severity: Medium
Contest weight: 0.1218
Dataset id: 4048
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Privileged addresses have authority over many functions that may be used to negatively disrupt the project. Some important privileges include:
GoldenGate
owner can withdraw all funds.
owner can set admins which are able to dilute allocation of other pools.
owner can set the migrator contract which can lead to loss of LP if malicious.
TokenVesting
owner can arbitrarily set the fee and fee address which can lead to loss of user funds.
BridgesRef
feeToSetter can arbitrarily set the distribution rate.
feeToSetter can withdraw any ERC-20 token in the contract.
BridgesRouter
feeSetter can set a arbitrary referral and dividend tracker contract.
BridgesFactory
feeToSetter can set an arbitrary start time for when a pair can be tradeable.

## Recommendation
Ensure that the privileged addresses are multi-sig and/or introduce timelock for improved community oversight. Optionally introduce require statements to limit the scope of the exploits that can be carried out by the privileged addresses.
