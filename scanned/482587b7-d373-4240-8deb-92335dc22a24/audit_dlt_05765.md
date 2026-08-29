# [H] # IOP _ ThunderNFT 34943 - [Smart Contract - High] User cant withdraw asset from pool after asset_mana

## Summary
Severity: High
Chain: Smart contract
Component: ThunderNFT | IOP
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ThunderNFT%20%7C%20IOP/IOP%20_%20ThunderNFT%2034943%20-%20%5BSmart%20Contract%20-%20High%5D%20User%20cant%20withdraw%20asset%20from%20pool%20after%20asset_managerremove_asset%20is%20called.md
Type: immunefi-boost

## Details
Target: https://github.com/ThunderFuel/smart-contracts/tree/main/contracts-v1/pool

## Description

## Brief/Intro

`asset_manager.add_asset` and `asset_manager.remove_asset` are used to control which asset are allowed in the pool. And when `pool.deposit` and `pool.withdraw` are called, the functions checks if the assetId is supported by `asset_manager.is_asset_supported`.

However there is an issue that after `asset_manager.remove_asset` is called, the corresponding asset in the pool can't be withdrawn.

## Vulnerability Details

As shown in [pool.withdraw](https://github.com/ThunderFuel/smart-contracts/blob/260c9859e2cd28c188e8f6283469bcf57c9347de/contracts-v1/pool/src/main.sw#L105-L124), when a user calls the function to withdraw asset, the function will check if the asset is supported in [pool#L112](https://github.com/ThunderFuel/smart-contracts/blob/260c9859e2cd28c188e8f6283469bcf57c9347de/contracts-v1/pool/src/main.sw#L112), and if not, the function will revert.

```Rust
105     fn withdraw(asset: AssetId, amount: u64) {
106         let sender = msg_sender().unwrap();
107         let current_balance = _balance_of(sender, asset);
108         require(current_balance >= amount, PoolErrors::AmountHigherThanBalance);
109 
110         let asset_manager_addr = storage.asset_manager.read().unwrap().bits();
111         let asset_manager = abi(AssetManager, asset_manager_addr);
112         require(asset_manager.is_asset_supported(asset), PoolErrors::AssetNotSupported); <<<<<----- here checks if the assetId is supported by asset_manager
113 
114         let new_balance = current_balance - amount;
115         storage.balance_of.insert((sender, asset), new_balance);
116 
117         transfer(sender, asset, amount);
118 
119         log(Withdrawal {
120             address: sender,
121             asset,
122             amount,
123         });
124     }
```

## Impact Details

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ThunderNFT%20%7C%20IOP/IOP%20_%20ThunderNFT%2034943%20-%20%5BSmart%20Contract%20-%20High%5D%20User%20cant%20withdraw%20asset%20from%20pool%20after%20asset_managerremove_asset%20is%20called.md_
