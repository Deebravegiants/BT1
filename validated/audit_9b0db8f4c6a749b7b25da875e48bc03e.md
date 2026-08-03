No vulnerability found for this question.

**Why this doesn't hold up:**

1. **No unprivileged entrypoint exists.** `randomness_config::set_for_next_epoch` — the only path that pushes a `RandomnessConfig` into `config_buffer` — requires `system_addresses::assert_aptos_framework(framework)`, i.e. it can only be invoked via a resolved governance proposal signed by the `@aptos_framework` signer, not by an arbitrary unprivileged caller. [1](#0-0) 

2. **`create_from_rational` is called before `new_v1`/`new_v2`, not inside them.** `new_v1`/`new_v2` merely wrap already-built `FixedPoint64` values; they perform no arithmetic and cannot abort. [2](#0-1) 
The `fixed_point64::create_from_rational` call (with its zero-denominator or out-of-range checks) happens earlier in the calling governance script, e.g. `fixed_point64::create_from_rational(1, 2)`, before `new_v1`/`set_for_next_epoch` is ever reached. [3](#0-2)  If the arithmetic aborts, execution never proceeds to `set_for_next_epoch`/`config_buffer::upsert` at all.

3. **Move transactions do not allow partial writes to survive an abort.** The Move VM buffers all resource mutations for a transaction in an in-memory session and only commits the writeset atomically upon successful (non-aborting) completion; an `assert!`/arithmetic abort discards the entire uncommitted session, so `config_buffer::upsert`'s single atomic `SimpleMap` upsert can never be left half-applied. [4](#0-3) 
This is also reflected in the formal spec, which shows `upsert` as an all-or-nothing state transition with no partial-write behavior. [5](#0-4) 

4. **No custody/asset impact.** `RandomnessConfig` is a governance-controlled system parameter, not an object, fungible asset, or token store; there is no `owner`, `store`, or capability transfer implicated here, so even a successful corruption of this buffer would not change who can own, move, mint, burn, or freeze APT or any asset. `on_new_epoch` only reads the buffer under a friend-only, `@aptos_framework`-gated call. [6](#0-5) 

Because the path requires the privileged `@aptos_framework` signer, arithmetic checks in `create_from_rational` run and abort strictly before any config-buffer mutation, Move's atomic commit semantics preclude partial writes, and no custody/ownership surface for APT, fungible assets, or token objects is touched, this does not meet the review's custody-impact bar.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/configs/randomness_config.move (L51-55)
```text
    /// This can be called by on-chain governance to update on-chain consensus configs for the next epoch.
    public fun set_for_next_epoch(framework: &signer, new_config: RandomnessConfig) {
        system_addresses::assert_aptos_framework(framework);
        config_buffer::upsert(new_config);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/configs/randomness_config.move (L57-68)
```text
    /// Only used in reconfigurations to apply the pending `RandomnessConfig`, if there is any.
    public(friend) fun on_new_epoch(framework: &signer) acquires RandomnessConfig {
        system_addresses::assert_aptos_framework(framework);
        if (config_buffer::does_exist<RandomnessConfig>()) {
            let new_config = config_buffer::extract_v2<RandomnessConfig>();
            if (exists<RandomnessConfig>(@aptos_framework)) {
                *borrow_global_mut<RandomnessConfig>(@aptos_framework) = new_config;
            } else {
                move_to(framework, new_config);
            }
        }
    }
```

**File:** aptos-move/framework/aptos-framework/sources/configs/randomness_config.move (L92-114)
```text
    public fun new_v1(secrecy_threshold: FixedPoint64, reconstruction_threshold: FixedPoint64): RandomnessConfig {
        RandomnessConfig {
            variant: copyable_any::pack( ConfigV1 {
                secrecy_threshold,
                reconstruction_threshold
            } )
        }
    }

    /// Create a `ConfigV2` variant.
    public fun new_v2(
        secrecy_threshold: FixedPoint64,
        reconstruction_threshold: FixedPoint64,
        fast_path_secrecy_threshold: FixedPoint64,
    ): RandomnessConfig {
        RandomnessConfig {
            variant: copyable_any::pack( ConfigV2 {
                secrecy_threshold,
                reconstruction_threshold,
                fast_path_secrecy_threshold,
            } )
        }
    }
```

**File:** aptos-move/aptos-release-builder/data/proposals/enable_randomness.move (L14-18)
```text
        let config = randomness_config::new_v1(
            fixed_point64::create_from_rational(1, 2), // secrecy_threshold: 1/2
            fixed_point64::create_from_rational(2, 3), // reconstruct_threshold: 2/3
        );
        randomness_config::set_for_next_epoch(&framework, config);
```

**File:** aptos-move/framework/aptos-framework/sources/configs/config_buffer.move (L69-74)
```text
    public(friend) fun upsert<T: drop + store>(config: T) acquires PendingConfigs {
        let configs = borrow_global_mut<PendingConfigs>(@aptos_framework);
        let key = type_info::type_name<T>();
        let value = any::pack(config);
        configs.configs.upsert(key, value);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/configs/config_buffer.spec.move (L35-44)
```text
    spec upsert<T: drop + store>(config: T) {
        pragma opaque;
        aborts_if !exists<PendingConfigs>(@aptos_framework);
        modifies global<PendingConfigs>(@aptos_framework);

        let key = type_info::type_name<T>();
        let post configs_post = global<PendingConfigs>(@aptos_framework).configs;
        ensures simple_map::spec_contains_key(configs_post, key);
        ensures simple_map::spec_get(configs_post, key) == any::pack(config);
    }
```
