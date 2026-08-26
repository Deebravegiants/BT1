# [M] Tapioca Bar: Unusable Market Add Functions in Penrose Contract

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1158
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/Penrose.sol#L381-L388
https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/Penrose.sol#L414-L421
https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/Penrose.sol#L438-L443


# Vulnerability details


The Penrose contract includes two market add functions, `addSingularity` and `addBigBang`, that are currently unusable and lack the necessary logic to function properly. These functions are intended to manually add Singularity and BigBang markets to the Penrose contract (After they are initialized with [`Singularity.sol#init`](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/Singularity.sol#L61-L98) and [`BigBang.sol#init`](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/bigBang/BigBang.sol#L100-L129), both of which take an `IPenrose tapiocaBar_` as a parameter and assign it to the `penrose` variable, the `owner` is set to the address of the `penrose` contract. This initialization process is crucial for the proper functioning of the markets within the Penrose contract).


## Impact

The impact of these issues is significant and affects the usability and security of The Tapioca Bar:

- **Malfunctioning Markets**: Due to the missing update of the `masterContractOf` mapping, markets added manually through `addSingularity` and `addBigBang` functions will not function as intended. This means that users will not be able to interact with these markets properly, resulting in potential loss of funds or assets stuck in non-functional markets.

- **Security Risks**: Accumulating unmanageable markets increases the attack surface of the contract, potentially leading to security vulnerabilities. Unused or malfunctioning markets could be exploited by malicious actors, posing a risk to the assets and funds of users.

## PoC

1. **Missing Update of `masterContractOf` Mapping**: When using the `addSingularity` and `addBigBang` functions to manually add markets, the `masterContractOf` mapping is not updated. This mapping is crucial for the proper functioning of the `executeMarketFn` function due to [this validation](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/Penrose.sol#L438C13-L443C15), which depends on `masterContractOf` to identify the correct market contract. As a result, markets added manually through these functions are not recognized, leading to malfunctioning markets and potential loss of funds.

2. **No Reversibility**: The current implementation lacks an undo or delete functionality for markets added through `addSingularity` and `addBigBang`. Once a market is added, there is no built-in mechanism to remove or disable it,  making it difficult to manage markets that were added with the issue mentioned above effectively. This can result in an accumulation of unmanageable markets, potentially leading to confusion, and a higher risk of security vulnerabilities.

## Tools Used

Manual Analysis

## Recommended Mitigation Steps

Modify the `addSingularity` and `addBigBang` functions to include an update to the **`masterContractOf` Mapping** when manually adding a market. This ensures that markets added through these functions are correctly recognized by the `executeMarketFn` function, allowing users to interact with them seamlessly.

```diff
function addSingularity(address mc, address _contract) external onlyOwner registeredSingularityMasterContract(mc) {
    isMarketRegistered[_contract] = true;
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1158_
