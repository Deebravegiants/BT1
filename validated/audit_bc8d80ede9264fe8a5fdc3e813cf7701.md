No vulnerability found for this question.

**Analysis:**

The `RELEASE_V1_50` gate in `native_exists_at` is the *fix* for a discovered issue (a closure/function type can carry a `key` ability annotation and satisfy `T: key`, as demonstrated by the `closure_key_address_to_object.masm` test), not a bypassable guard that an attacker can trigger on current mainnet. [1](#0-0) 

Two facts undermine the proof idea:

1. **The claimed consequence is wrong.** Even in the pre-fix code path (no `is_struct_or_enum` check), passing a non-struct type into `context.exists_at` does not produce an "incorrect" existence result or corrupt ownership state — it hits `create_data_cache_entry`'s struct-tag conversion, which returns `Err(PartialVMError::new(StatusCode::INTERNAL_TYPE_ERROR))` for any non-struct `TypeTag`. This surfaces as an invariant violation that aborts the transaction deterministically; it never returns a wrong boolean or corrupts the resource read for `address_to_object`. [2](#0-1) 

2. **The gated code path isn't reachable by an unprivileged attacker on current mainnet.** `gas_feature_version` is a network-wide on-chain parameter controlled by governance (`GasScheduleV2`), not something a transaction sender can select per-call. `LATEST_GAS_FEATURE_VERSION` is defined as `RELEASE_V1_50` itself, meaning the fix is baked into the same release that introduces the constant — there is no reachable production configuration where the guard is compiled in but gas_feature_version is set below `RELEASE_V1_50`. [3](#0-2) 

Since the worst-case outcome is a deterministic transaction abort (invariant violation) rather than an incorrect ownership/balance resolution, and the gating condition isn't attacker-controllable, this does not cross a custody boundary per the review's decision standard.

### Citations

**File:** aptos-move/framework/natives/src/object.rs (L90-100)
```rust
    context.charge(OBJECT_EXISTS_AT_BASE)?;

    // Only structs can be resources in global storage. A non-struct type (e.g., a function type
    // that declared the `key` ability) would reach the data cache and trip a VM invariant
    // violation, so reject it here with a deterministic, kept abort instead.
    if context.gas_feature_version() >= RELEASE_V1_50 && !type_.is_struct_or_enum() {
        return Err(SafeNativeError::abort_with_message(
            ENOT_A_RESOURCE_TYPE,
            "Object type argument must be a resource (struct) type",
        ));
    }
```

**File:** third_party/move/move-vm/runtime/src/data_cache.rs (L313-319)
```rust
        let struct_tag = match module_storage.runtime_environment().ty_to_ty_tag(ty)? {
            TypeTag::Struct(struct_tag) => *struct_tag,
            _ => {
                // Since every resource is a struct, the tag must be also a struct tag.
                return Err(PartialVMError::new(StatusCode::INTERNAL_TYPE_ERROR));
            },
        };
```

**File:** aptos-move/aptos-gas-schedule/src/ver.rs (L89-133)
```rust
pub const LATEST_GAS_FEATURE_VERSION: u64 = gas_feature_versions::RELEASE_V1_50;

pub mod gas_feature_versions {
    pub const RELEASE_V1_8: u64 = 11;
    pub const RELEASE_V1_9_SKIPPED: u64 = 12;
    pub const RELEASE_V1_9: u64 = 13;
    pub const RELEASE_V1_10: u64 = 15;
    pub const RELEASE_V1_11: u64 = 16;
    pub const RELEASE_V1_12: u64 = 17;
    pub const RELEASE_V1_13: u64 = 18;
    pub const RELEASE_V1_14: u64 = 19;
    pub const RELEASE_V1_15: u64 = 20;
    pub const RELEASE_V1_16: u64 = 21;
    pub const RELEASE_V1_18: u64 = 22;
    pub const RELEASE_V1_19: u64 = 23;
    pub const RELEASE_V1_20: u64 = 24;
    pub const RELEASE_V1_21: u64 = 25;
    pub const RELEASE_V1_22: u64 = 26;
    pub const RELEASE_V1_23: u64 = 27;
    pub const RELEASE_V1_24: u64 = 28;
    pub const RELEASE_V1_26: u64 = 30;
    pub const RELEASE_V1_27: u64 = 31;
    pub const RELEASE_V1_28: u64 = 32;
    pub const RELEASE_V1_29: u64 = 33;
    pub const RELEASE_V1_30: u64 = 34;
    pub const RELEASE_V1_31: u64 = 35;
    pub const RELEASE_V1_32: u64 = 36;
    pub const RELEASE_V1_33: u64 = 37;
    pub const RELEASE_V1_34: u64 = 38;
    pub const RELEASE_V1_35: u64 = 39;
    pub const RELEASE_V1_36: u64 = 40;
    pub const RELEASE_V1_37: u64 = 41;
    pub const RELEASE_V1_38: u64 = 42;
    pub const RELEASE_V1_39: u64 = 43;
    pub const RELEASE_V1_40: u64 = 44;
    pub const RELEASE_V1_41: u64 = 45;
    pub const RELEASE_V1_42: u64 = 46;
    pub const RELEASE_V1_43: u64 = 47;
    pub const RELEASE_V1_44: u64 = 48;
    pub const RELEASE_V1_45: u64 = 49;
    pub const RELEASE_V1_46: u64 = 50;
    pub const RELEASE_V1_47: u64 = 51;
    pub const RELEASE_V1_48: u64 = 52;
    pub const RELEASE_V1_49: u64 = 53;
    pub const RELEASE_V1_50: u64 = 54;
```
