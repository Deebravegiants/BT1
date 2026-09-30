# [M] LiquidityProvider can also lend to Private-

## Summary
Severity: Medium
Contest weight: 0.0975
Dataset id: 17727
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Insufficient access control for lending to PublicVault found by yawn-c111 Docs says as follows https://docs.astaria.xyz/docs/intro Any strategists may provide their own capital to fund these loans through their own PrivateVaults, and whitelisted strategists can deploy PublicVaults that accept funds from other liquidity providers. However, Liquidity Providers can also lend to PrivateVault. This is because lendToVault function is controlled by mapping(address => address) public vaults, which are managed by _newVault function and include PrivateVaults. This leads to unexpected atttack. Unexpected liquidity providers can lend to private vaults

## Recommendation
create requirement to lend to only PublicVaults.
