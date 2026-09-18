I found the direct analog: `TargetOrders::load_mut` is called in `process_initialize2` (the pool-creator-reachable path) **before** any length/owner validation, unlike every other call site in the codebase which uses the checked wrapper `load_mut_checked`.

### Title
Out-of-bounds struct read in Initialize2 via unchecked `TargetOrders::load_mut` on attacker-sized account - (File: `program/src/processor.rs`)

### Summary
The DHCP-parsing CVE's root cause is reading a fixed-format structure out of an externally-controlled buffer without first validating that the buffer is large enough to hold the structure, causing an out-of-bounds memory read. Raydium's `Loadable::load_mut`/`load` trait methods do the analogous unchecked reinterpret-cast of raw account bytes into a fixed-size struct via `bytemuck::from_bytes_mut`/`from_bytes` with no length check [1](#0-0) . Every other call site in the program wraps this with `load_mut_checked`/`load_checked`, which first verifies `account.data_len() == size_of::<Self>()` [2](#0-1) [3](#0-2) . However, in `process_initialize2` the target-orders account is loaded with the **unchecked** `TargetOrders::load_mut(amm_target_orders_info)?` right after only an owner check, with no `data_len()` verification [4](#0-3) .

### Finding Description
`process_initialize2` is reachable by any unprivileged pool creator submitting an `Initialize2` instruction with attacker-chosen accounts. The target-orders account is normally created just before this call via `generate_amm_associated_account` with `size_of::<TargetOrders>()` [5](#0-4) , but the code path that consumes it only checks:
```
if amm_target_orders_info.owner != program_id {
    return Err(AmmError::InvalidProgramAddress.into());
}
let mut target_order = TargetOrders::load_mut(amm_target_orders_info)?;
``` [4](#0-3) 
`load_mut` performs `bytemuck::from_bytes_mut(data)` on the raw account data without checking `data.len() == size_of::<TargetOrders>()` [6](#0-5) . `bytemuck::from_bytes_mut` will panic if the slice is shorter than the target type, but if the slice is *longer* than the struct (e.g. an oversized account owned by the program with data padding after it, or any account whose owner was set to `program_id` and whose length happens to exceed `size_of::<TargetOrders>()`), the cast silently succeeds and reads/writes fields (`calc_pnl_x`, `calc_pnl_y`, `owner`, etc.) using whatever bytes are actually present at those offsets — the analog of the DHCP parser trusting a length/offset without validating the buffer bound before interpreting the reply as a fixed layout.

### Impact Explanation
`target_order.check_init(...)` writes calculated pnl accounting values (`calc_pnl_x`, `calc_pnl_y`, `owner`) into whatever memory backs this improperly-sized account [7](#0-6) , and this same account is subsequently trusted as the authoritative `target_orders` for all withdraw/swap pnl accounting via `load_mut_checked` elsewhere (which does enforce exact size on later calls). If the initial unchecked write establishes a `TargetOrders` structure backed by a data region whose true size/layout diverges from the `#[repr(C, packed)]` layout assumed by the struct (e.g., because it wasn't actually pre-sized by `generate_amm_associated_account` but the caller supplies a differently-sized account they also own via some other path), pnl bookkeeping (`calc_pnl_x`/`calc_pnl_y`) can become corrupted/incoherent with the pool's real vault balances, and this data is the basis for `WithdrawPnl`'s protocol pnl accounting and withdraw's LP calc-pnl updates [8](#0-7) .

### Likelihood Explanation
Reaching this requires initializing a pool (`Initialize2`), an action any unprivileged pool creator can perform in a single transaction. Because `generate_amm_associated_account` in the same instruction handler creates the target-orders account at the exact expected size right before the unchecked load, exploiting a size mismatch would require the attacker to substitute a different, pre-existing account they own that happens to already be assigned as owner == `program_id` with a different length — which is difficult to arrange organically. This significantly limits practical exploitability compared to the theoretical bug class from the CVE.

### Recommendation
Replace the unchecked `TargetOrders::load_mut(amm_target_orders_info)?` call in `process_initialize2` with `TargetOrders::load_mut_checked`-style validation (verify `account.data_len() == size_of::<TargetOrders>()` and `account.owner == program_id`) before casting the bytes, consistent with every other call site in the codebase.

### Proof of Concept
Not concretely demonstrable from static analysis alone: the exploitability hinges on whether an attacker can supply, at `Initialize2` time, a `target_orders_info` account that (a) is owned by the AMM `program_id` and (b) has a data length different from `size_of::<TargetOrders>()`, before `generate_amm_associated_account` allocates it at the correct size in the same instruction. Given the account is freshly created via a PDA/associated-account derivation in the same call, this pre-condition could not be confirmed as reachable with the available tooling; a dynamic/on-chain test against `generate_amm_associated_account`'s account creation and re-initialization semantics would be needed to confirm or refute exploitability.

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

**File:** program/src/state.rs (L152-178)
```rust
    pub fn check_init(&mut self, x: u128, y: u128, owner: &Pubkey) -> Result<(), ProgramError> {
        if self.owner != Pubkey::default() {
            return Err(AmmError::AlreadyInUse.into());
        }
        self.owner = *owner;
        self.last_order_numerator = 0; // 3
        self.last_order_denominator = 0; // 1

        self.plan_orders_cur = 0;
        self.place_orders_cur = 0;

        self.valid_buy_order_num = 0;
        self.valid_sell_order_num = 0;

        self.target_x = 0;
        self.target_y = 0;
        self.plan_x_buy = 0;
        self.plan_y_buy = 0;
        self.plan_x_sell = 0;
        self.plan_y_sell = 0;
        self.placed_x = 0;
        self.placed_y = 0;
        self.calc_pnl_x = x;
        self.calc_pnl_y = y;
        self.free_slot_bits = std::u128::MAX;
        Ok(())
    }
```

**File:** program/src/state.rs (L180-198)
```rust
    /// load_mut_checked
    #[inline]
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

**File:** program/src/state.rs (L677-696)
```rust
impl AmmInfo {
    /// Helper function to get the more efficient packed size of the struct
    /// load_mut_checked
    #[inline]
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

**File:** program/src/processor.rs (L960-965)
```rust
        // check and init target orders account
        if amm_target_orders_info.owner != program_id {
            return Err(AmmError::InvalidProgramAddress.into());
        }
        let mut target_order = TargetOrders::load_mut(amm_target_orders_info)?;
        target_order.check_init(x.as_u128(), y.as_u128(), amm_info.key)?;
```

**File:** program/src/processor.rs (L1818-1839)
```rust
        // step4: update target_orders.calc_pnl_x & target_orders.calc_pnl_y
        target_orders.calc_pnl_x = x1
            .checked_sub(Calculator::normalize_decimal_v2(
                pc_amount,
                amm.pc_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_x))
            .unwrap()
            .as_u128();
        target_orders.calc_pnl_y = y1
            .checked_sub(Calculator::normalize_decimal_v2(
                coin_amount,
                amm.coin_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_y))
            .unwrap()
            .as_u128();
        amm.recent_epoch = Clock::get()?.epoch;
```
