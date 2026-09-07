# [H] # IOP _ ThunderNFT 34587 - [Smart Contract - High] Users might temporarily get their funds locked in P

## Summary
Severity: High
Chain: Smart contract
Component: ThunderNFT | IOP
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ThunderNFT%20%7C%20IOP/IOP%20_%20ThunderNFT%2034587%20-%20%5BSmart%20Contract%20-%20High%5D%20Users%20might%20temporarily%20get%20their%20funds%20locked%20in%20Pool%20contract.md
Type: immunefi-boost

## Details
Target: https://github.com/ThunderFuel/smart-contracts/tree/main/contracts-v1/pool

## Description

## Brief/Intro

The `Pool` contract allows deposits and withdrawals of assets. Assets must be whitelisted within `AssetManager` contract. The `withdraw()` method is verifying if an asset is whitelisted, hence once it gets removed from the `AssetManager` users cannot withdraw them.

## Vulnerability Details

The `withdraw()` method is unnecessarily checking whether an asset is whitelisted with `AssetManager` contract by calling `is_asset_supported()` as per the code snippet below:

```
fn withdraw(asset: AssetId, amount: u64) {
        [...]
        require(asset_manager.is_asset_supported(asset), PoolErrors::AssetNotSupported);
        [...]
    }
```

Hence if a protocol decided to delist an asset which is already deposited by a user, the user cannot withdraw their funds. In order to withdraw the funds the contract owner would need to again whitelist an asset by calling `add_asset()` in the `AssetManager` contract.

## Impact Details

User funds get stuck when the situation above happens in the contract and the only way to get them out is that the contract owner reacts and puts the asset back on the whitelist. Depending on the protocol teams reaction this can easily go above 1 hour hence the impact is High.

While it is possible to recover from the situation by protocol team's reaction, the "emergency" whitelisting previously de-listed asset could cause some other users to deposit the unwanted asset, and hence the problem might continue.

## Solution proposal

Allow withdrawal of assets regardless if they are whitelisted or not.

## References

The line causing the issue: https://github.com/ThunderFuel/smart-contracts/blob/260c9859e2cd28c188e8f6283469bcf57c9347de/contracts-v1/pool/src/main.sw#L112

## Proof of concept


_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ThunderNFT%20%7C%20IOP/IOP%20_%20ThunderNFT%2034587%20-%20%5BSmart%20Contract%20-%20High%5D%20Users%20might%20temporarily%20get%20their%20funds%20locked%20in%20Pool%20contract.md_
