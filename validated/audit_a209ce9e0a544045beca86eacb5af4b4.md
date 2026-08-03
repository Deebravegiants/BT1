No vulnerability found for this question.

**Rationale:**

1. **The `Features` resource cannot be written by unprivileged callers.** Setting or changing feature flags on-chain requires a call through `change_feature_flags_internal`, gated by `ensure_framework_signer`, which asserts `signer::address_of(account) == @std` [1](#0-0) . Applying pending changes via `on_new_epoch` is likewise restricted to the framework signer [2](#0-1) . There is no unprivileged transaction, entry function, or bytecode path that lets an attacker write arbitrary/malformed bytes into the `Features` resource.

2. **Even if the underlying bitset were corrupted, the relevant Move-level check for this flag is hardcoded and no longer reads the bitset.** `object_native_derived_address_enabled()` unconditionally returns `true` and is marked `#[deprecated]`, rather than calling `is_enabled(OBJECT_NATIVE_DERIVED_ADDRESS)` [3](#0-2) . The flag's comment in the Rust enum confirms this: "Feature rolled out, no longer can be disabled" [4](#0-3) .

3. **The actual native address-derivation code path never consults `Features::is_enabled` for this flag at all.** `native_create_user_derived_object_address_impl` in the natives crate computes the derived address unconditionally via `AuthenticationKey::object_address_from_object`, with no feature-flag branch present in the current code [5](#0-4) . So there is no code path where a cleared bit for `_OBJECT_NATIVE_DERIVED_ADDRESS` produces "an alternate, attacker-influenced derived address" — the derivation logic doesn't branch on this flag anymore.

Given that (a) unprivileged actors cannot write to the `Features` resource, and (b) the custody-relevant address-derivation logic no longer branches on this specific flag in either the Move framework or the native implementation, there is no real custody boundary crossed. The premise of the question — that toggling this bit changes derived-address computation — does not hold against the current codebase.

### Citations

**File:** aptos-move/framework/move-stdlib/sources/configs/features.move (L565-568)
```text
    #[deprecated]
    public fun object_native_derived_address_enabled(): bool {
        true
    }
```

**File:** aptos-move/framework/move-stdlib/sources/configs/features.move (L1078-1088)
```text
    public fun on_new_epoch(framework: &signer) acquires Features, PendingFeatures {
        ensure_framework_signer(framework);
        if (exists<PendingFeatures>(@std)) {
            let PendingFeatures { features } = move_from<PendingFeatures>(@std);
            if (exists<Features>(@std)) {
                Features[@std].features = features;
            } else {
                move_to(framework, Features { features })
            }
        }
    }
```

**File:** aptos-move/framework/move-stdlib/sources/configs/features.move (L1124-1127)
```text
    fun ensure_framework_signer(account: &signer) {
        let addr = signer::address_of(account);
        assert!(addr == @std, error::permission_denied(EFRAMEWORK_SIGNER_NEEDED));
    }
```

**File:** types/src/on_chain_config/aptos_features.rs (L84-85)
```rust
    // Feature rolled out, no longer can be disabled.
    _OBJECT_NATIVE_DERIVED_ADDRESS = 62,
```

**File:** aptos-move/framework/natives/src/object.rs (L124-147)
```rust
fn native_create_user_derived_object_address_impl(
    context: &mut SafeNativeContext,
    ty_args: &[Type],
    mut args: VecDeque<Value>,
) -> SafeNativeResult<SmallVec<[Value; 1]>> {
    debug_assert!(ty_args.is_empty());
    debug_assert!(args.len() == 2);

    context.charge(OBJECT_USER_DERIVED_ADDRESS_BASE)?;

    let object_context = context.extensions().get::<NativeObjectContext>();
    let derive_from = safely_pop_arg!(args, AccountAddress);
    let source = safely_pop_arg!(args, AccountAddress);

    let derived_address = *object_context
        .derived_from_object_addresses
        .borrow_mut()
        .entry((derive_from, source))
        .or_insert_with(|| {
            AuthenticationKey::object_address_from_object(&source, &derive_from).account_address()
        });

    Ok(smallvec![Value::address(derived_address)])
}
```
