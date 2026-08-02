No vulnerability found for this question.

**Reasoning:** Both `set_for_next_epoch` and `set_for_next_epoch_check_hash` in `gas_schedule.move` require `system_addresses::assert_aptos_framework(aptos_framework)` before ever touching `config_buffer::upsert`, meaning the caller must already possess the `@aptos_framework` signer — obtainable only through the on-chain governance execution path, not by any unprivileged transaction, package, view, authenticator, API, bytecode, or proof input. [1](#0-0) [2](#0-1) 

The scenario described — a "confused/compromised-adjacent governance flow" calling both setters within one epoch — requires pre-existing privileged governance access to invoke either function, which the review bounds explicitly exclude ("privileged governance or admin assumptions"). Additionally, `config_buffer::upsert` intentionally uses a `SimpleMap::upsert` (last-write-wins) design by construction — this is documented, expected behavior for buffering the next-epoch config, not a custody boundary violation. [3](#0-2) 

Even granting the described sequence, the "hash-checked guarantee" is a governance safety-net (protecting against a stale-schedule race between multiple governance proposals), not a custody guarantee over APT, fungible assets, token objects, multisig, or resource-account authority. No balance, owner, authority, or recovery right changes as a result — `on_new_epoch` simply applies whichever `GasScheduleV2` is last in the buffer, which affects VM gas pricing, not asset ownership or control. [4](#0-3) 

This fails the Custody Impact Gate (no theft/mint/burn/freeze/ownership reassignment) and fails the Review Bounds (requires pre-existing governance/admin privilege, not an unprivileged entrypoint).

### Citations

**File:** aptos-move/framework/aptos-framework/sources/configs/gas_schedule.move (L90-102)
```text
    public fun set_for_next_epoch(aptos_framework: &signer, gas_schedule_blob: vector<u8>) acquires GasScheduleV2 {
        system_addresses::assert_aptos_framework(aptos_framework);
        assert!(!gas_schedule_blob.is_empty(), error::invalid_argument(EINVALID_GAS_SCHEDULE));
        let new_gas_schedule: GasScheduleV2 = from_bytes(gas_schedule_blob);
        if (exists<GasScheduleV2>(@aptos_framework)) {
            let cur_gas_schedule = borrow_global<GasScheduleV2>(@aptos_framework);
            assert!(
                new_gas_schedule.feature_version >= cur_gas_schedule.feature_version,
                error::invalid_argument(EINVALID_GAS_FEATURE_VERSION)
            );
        };
        config_buffer::upsert(new_gas_schedule);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/configs/gas_schedule.move (L107-131)
```text
    public fun set_for_next_epoch_check_hash(
        aptos_framework: &signer,
        old_gas_schedule_hash: vector<u8>,
        new_gas_schedule_blob: vector<u8>
    ) acquires GasScheduleV2 {
        system_addresses::assert_aptos_framework(aptos_framework);
        assert!(!new_gas_schedule_blob.is_empty(), error::invalid_argument(EINVALID_GAS_SCHEDULE));

        let new_gas_schedule: GasScheduleV2 = from_bytes(new_gas_schedule_blob);
        if (exists<GasScheduleV2>(@aptos_framework)) {
            let cur_gas_schedule = borrow_global<GasScheduleV2>(@aptos_framework);
            assert!(
                new_gas_schedule.feature_version >= cur_gas_schedule.feature_version,
                error::invalid_argument(EINVALID_GAS_FEATURE_VERSION)
            );
            let cur_gas_schedule_bytes = bcs::to_bytes(cur_gas_schedule);
            let cur_gas_schedule_hash = aptos_hash::sha3_512(cur_gas_schedule_bytes);
            assert!(
                cur_gas_schedule_hash == old_gas_schedule_hash,
                error::invalid_argument(EINVALID_GAS_SCHEDULE_HASH)
            );
        };

        config_buffer::upsert(new_gas_schedule);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/configs/gas_schedule.move (L134-144)
```text
    public(friend) fun on_new_epoch(framework: &signer) acquires GasScheduleV2 {
        system_addresses::assert_aptos_framework(framework);
        if (config_buffer::does_exist<GasScheduleV2>()) {
            let new_gas_schedule = config_buffer::extract_v2<GasScheduleV2>();
            if (exists<GasScheduleV2>(@aptos_framework)) {
                *borrow_global_mut<GasScheduleV2>(@aptos_framework) = new_gas_schedule;
            } else {
                move_to(framework, new_gas_schedule);
            }
        }
    }
```

**File:** aptos-move/framework/aptos-framework/sources/configs/config_buffer.move (L66-74)
```text
    /// Upsert an on-chain config to the buffer for the next epoch.
    ///
    /// Typically used in `X::set_for_next_epoch()` where X is an on-chain config.
    public(friend) fun upsert<T: drop + store>(config: T) acquires PendingConfigs {
        let configs = borrow_global_mut<PendingConfigs>(@aptos_framework);
        let key = type_info::type_name<T>();
        let value = any::pack(config);
        configs.configs.upsert(key, value);
    }
```
