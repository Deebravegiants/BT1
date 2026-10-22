# [H] Precompiled Contract Not Updated

## Summary
Severity: High
Contest weight: 0.2788
Dataset id: 14402
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The precompiled contract tssreward.go in L2geth, scheduled for implementation at chain genesis, exhibits inconsistencies with its corresponding source code packages/contracts/contracts/L2/predeploys/TssRewardContract.sol in
the parameters of certain functions and the absence of some functions, as indicated by the ABI on line [33].
Within the L2geth framework, a set of precompiled contracts are intended to be deployed on-chain during the chain
genesis process. One of these contracts, namely tssreward.go, underwent its latest modification on November 11,
2022. Conversely, the corresponding source code file, located at
packages/contracts/contracts/L2/predeploys/TssRewardContract.sol was last edited on November 23, 2022.
Detecting the precise discrepancies between the two versions poses a challenge since tssreward.go solely contains
bytecode representation. However, a comparison of the ABI on line [33], reveals variations in the function parameters
and the absence of certain functions in tssreward.go.
Updating the TSS reward contract or its address would require a hard fork as both are stored within L2geth and so
would alter consensus. This hard fork could cause a chain split or further issues on-chain for contracts and users.

## Recommendation
Update the predeployed Golang contract tssreward.go with the correct bytecode and ABI information for the newer
Solidity contract.
