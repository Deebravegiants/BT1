# [H] VLT-2 | Vault Can Be Drained Through Overlooked Mint Function

## Summary
Severity: High
Contest weight: 0.2042
Dataset id: 20580
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The RestEthVault contract Vault has an adapter for each LST it supports, including for the flagship asset, that will be set as the ERC4626 vault asset. The contract mistakenly does not overwrite the ERC4626.mint(uint256,address) function, meaning that when receiving shares through that function, the required asset LST asset amount will be mapped as a parity of 1:1 with ETH. If the flagship LST has a moment when it is valued higher than ETH, by depositing through this function an attacker could then instantly resell the shares, using the withdrawUsingAssets function for a profit, after fees. The attack would require that funds be existing in the vault, thus back-running any deposit call and would require the difference in price in the flagship LST and ETH so that it is profitable after withdraw fees.

## Recommendation
Override the ERC4626.mint(uint256,address) function and use the adapter provided price.
