### Title
Panic-inducing untrusted-size struct cast (untrusted "pointer"/size dereference) in `Loadable::load_mut`/`load` used by `Initialize2` swap/deposit/withdraw paths - (File: `program/src/state.rs`)

### Summary
The HDF5 CVE-2021-46243 bug class is an untrusted-pointer/size dereference during decoding of attacker-influenced data, causing the parser to read past what it validated and crash (DoS). The analogous pattern in this program is `Loadable::load_mut`/`load`, which directly casts raw account bytes into a fixed-size Pod struct via `bytemuck::from_bytes_mut`/`from_bytes` without first checking that the account's data length matches `size_of::<Self>()`.

### Finding Description
`Loadable::load_mut` and `Loadable::load` in [1](#0-0)  perform:
```
Ok(RefMut::map(account.try_borrow_mut_data()?, |data| from_bytes_mut(data)))
```
with a `// TODO verify if this checks for size` comment left directly above it, indicating the size check is known-missing. `bytemuck::from_bytes_mut`/`from_bytes` panics if the byte slice length does not exactly equal `size_of::<T>()`.

Most instruction handlers call the *checked* variants (`AmmInfo::load_mut_checked`, `TargetOrders::load_mut_checked`, `AmmConfig::load_mut_checked`), which do verify `account.data_len() == size_of::<Self>()` before calling the unchecked `load`/`load_mut`, e.g. [2](#0-1)  and [3](#0-2) .

However, `process_initialize2` calls the **unchecked** loaders directly on attacker-supplied, freshly-created PDAs before any size validation:
- `AmmInfo::load_mut(&amm_info)` at [4](#0-3) 
- `TargetOrders::load_mut(amm_target_orders_info)` at [5](#0-4) 

Both `amm_info` and `amm_target_orders_info` are created moments earlier via `Self::generate_amm_associated_account(..., size_of::<TargetOrders>())` / `size_of::<AmmInfo>()` at [6](#0-5)  and [7](#0-6) . I was not able to fully inspect `generate_amm_associated_account`'s implementation (its definition was not resolvable within the indexed content), so I cannot confirm from the available code whether it strictly rejects a pre-existing/pre-funded account of the wrong size versus tolerating an already-initialized account and skipping allocation. This is a meaningful gap in my verification.

### Impact Explanation
If an attacker can get `generate_amm_associated_account` to accept (or skip re-creating) a PDA that already exists with a byte length different from `size_of::<AmmInfo>()` or `size_of::<TargetOrders>()` — for instance by pre-funding/pre-allocating the deterministic PDA address with a wrong size before submitting `Initialize2` — the subsequent unchecked `load_mut` call would panic inside `bytemuck::from_bytes_mut` on account-length mismatch. A panic in a Solana program instruction aborts the transaction; if reachable by any attacker as part of the normal, permissionless pool-creation flow, this becomes a targeted DoS against pool creation for a chosen coin/pc pair (denial of a specific market), which is a Medium-severity availability impact, not fund theft.

### Likelihood Explanation
Likelihood is uncertain and depends entirely on the un-verified behavior of `generate_amm_associated_account`. If that helper unconditionally performs `create_account`/`allocate` via CPI to the System Program using the exact `size_of::<T>()` and always fails when the target account already has lamports/data (the standard Solana `system_instruction::create_account` behavior), then the wrong-size scenario cannot occur and this analog does not apply. I could not confirm this function's implementation with the available index, so I cannot assert the vulnerability is concretely reachable.

### Recommendation
- Remove the unchecked `Loadable::load`/`load_mut` bypass in `process_initialize2`; require a `data_len()` check (or use the existing `*_checked` variants) immediately before casting `amm_info` and `amm_target_orders_info` into their respective structs.
- Resolve the `// TODO verify if this checks for size` in `Loadable::load_mut`/`load` by adding an explicit `data_len() == size_of::<Self>()` assertion that returns a `ProgramError` instead of relying on `bytemuck` to panic.
- Confirm and, if necessary, harden `generate_amm_associated_account`/`generate_amm_associated_spl_mint`/`generate_amm_associated_spl_token` to reject any pre-existing account at the target PDA whose size or owner does not exactly match expectations, rather than silently reusing it.

### Proof of Concept
Not constructible with confidence from the indexed code alone: the exploit hinges on the exact allocation semantics of `generate_amm_associated_account`, whose source I could not retrieve via search/grep in this session (only its call sites were found). A concrete PoC would require: (1) confirming that function allows reuse of a pre-existing account of mismatched size for the `amm_target_orders_info` or `amm_info` PDA, then (2) submitting an `Initialize2` transaction referencing such a pre-created account to trigger the panic in `TargetOrders::load_mut`/`AmmInfo::load_mut`. [1](#0-0) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** program/src/state.rs (L39-55)
```rust
pub trait Loadable: Pod {
    fn load_mut<'a>(account: &'a AccountInfo) -> Result<RefMut<'a, Self>, ProgramError> {
        // TODO verify if this checks for size
        Ok(RefMut::map(account.try_borrow_mut_data()?, |data| {
            from_bytes_mut(data)
        }))
    }
    fn load<'a>(account: &'a AccountInfo) -> Result<Ref<'a, Self>, ProgramError> {
        Ok(Ref::map(account.try_borrow_data()?, |data| {
            from_bytes(data)
        }))
    }

    fn load_from_bytes(data: &[u8]) -> Result<&Self, ProgramError> {
        Ok(from_bytes(data))
    }
}
```

**File:** program/src/state.rs (L182-198)
```rust
    pub fn load_mut_checked<'a>(
        account: &'a AccountInfo,
        program_id: &Pubkey,
        owner: &Pubkey,
    ) -> Result<RefMut<'a, Self>, ProgramError> {
        if account.owner != program_id {
            return Err(AmmError::InvalidTargetAccountOwner.into());
        }
        if account.data_len() != size_of::<Self>() {
            return Err(AmmError::ExpectedAccount.into());
        }
        let data = Self::load_mut(account)?;
        if data.owner != *owner {
            return Err(AmmError::InvalidTargetOwner.into());
        }
        Ok(data)
    }
```

**File:** program/src/state.rs (L681-696)
```rust
    pub fn load_mut_checked<'a>(
        account: &'a AccountInfo,
        program_id: &Pubkey,
    ) -> Result<RefMut<'a, Self>, ProgramError> {
        if account.owner != program_id {
            return Err(AmmError::InvalidAmmAccountOwner.into());
        }
        if account.data_len() != size_of::<Self>() {
            return Err(AmmError::ExpectedAccount.into());
        }
        let data = Self::load_mut(account)?;
        if data.status == AmmStatus::Uninitialized as u64 {
            return Err(AmmError::InvalidStatus.into());
        }
        Ok(data)
    }
```

**File:** program/src/processor.rs (L747-758)
```rust
        // create target_order account
        Self::generate_amm_associated_account(
            program_id,
            program_id,
            market_info,
            amm_target_orders_info,
            user_wallet_info,
            system_program_info,
            rent_sysvar_info,
            TARGET_ASSOCIATED_SEED,
            size_of::<TargetOrders>(),
        )?;
```

**File:** program/src/processor.rs (L804-814)
```rust
        Self::generate_amm_associated_account(
            program_id,
            program_id,
            market_info,
            amm_info,
            user_wallet_info,
            system_program_info,
            rent_sysvar_info,
            AMM_ASSOCIATED_SEED,
            size_of::<AmmInfo>(),
        )?;
```

**File:** program/src/processor.rs (L843-847)
```rust
        // load AmmInfo
        let mut amm = AmmInfo::load_mut(&amm_info)?;
        if amm.status != AmmStatus::Uninitialized.into_u64() {
            return Err(AmmError::AlreadyInUse.into());
        }
```

**File:** program/src/processor.rs (L960-965)
```rust
        // check and init target orders account
        if amm_target_orders_info.owner != program_id {
            return Err(AmmError::InvalidProgramAddress.into());
        }
        let mut target_order = TargetOrders::load_mut(amm_target_orders_info)?;
        target_order.check_init(x.as_u128(), y.as_u128(), amm_info.key)?;
```
