Based on my investigation, this codebase does not contain an analogous vulnerability to CVE-2023-36054.

The krb5 bug class involves an RPC/XDR deserialization routine (`_xdr_kadm5_principal_ent_rec`) that trusts an attacker-supplied count field (`n_key_data`) without validating it against the actual size of a companion array (`key_data`), leading to freeing an uninitialized pointer. To be analogous in this program, there would need to be a reachable instruction path where a count/length field from instruction data or account data drives array indexing/allocation/freeing without being cross-validated against the actual backing buffer size.

Reviewing the in-scope surface:

- All account state loading (`AmmInfo::load_mut_checked`, `TargetOrders::load_mut_checked`, `AmmConfig::load_mut_checked`) enforces an exact fixed-size check (`account.data_len() != size_of::<Self>()`) before casting the account's byte buffer into a `Pod`/`bytemuck` struct, so there is no attacker-controlled "count" field that can decouple from the actual array size the way `n_key_data` does from `key_data` in the CVE. [1](#0-0) [2](#0-1) 

- `TargetOrders` contains fixed-size arrays (`buy_orders: [TargetOrder; 50]`, `sell_orders: [TargetOrder; 50]`, `replace_buy_client_id`/`replace_sell_client_id: [u64; MAX_ORDER_LIMIT]`) — these are compile-time fixed sizes, not driven by any runtime/attacker-supplied length field, so there's no equivalent of the `n_key_data`/`key_data` mismatch. [3](#0-2) 

- Instruction unpacking (`AmmInstruction::unpack`) for `Initialize2`, `Deposit`, `Withdraw`, `SwapBaseIn/Out`, and their V2 variants uses fixed-width `unpack_u8`/`unpack_u64` helpers with explicit `rest.len()` bounds checks before every read; there's no length-prefixed variable-size structure whose declared count could diverge from the actual payload.
<invoke name="grep_search">
<parameter name="pattern">unpack_u8|unpack_u64</parameter>
<parameter name="repo_name">AYontt/raydium-amm--009</parameter>
</invoke>

### Citations

**File:** program/src/state.rs (L82-99)
```rust
pub struct TargetOrders {
    pub owner: Pubkey,
    pub buy_orders: [TargetOrder; 50],
    pub padding1: [u64; 8],
    pub target_x: u128,
    pub target_y: u128,
    pub plan_x_buy: u128,
    pub plan_y_buy: u128,
    pub plan_x_sell: u128,
    pub plan_y_sell: u128,
    pub placed_x: u128,
    pub placed_y: u128,
    pub calc_pnl_x: u128,
    pub calc_pnl_y: u128,
    pub sell_orders: [TargetOrder; 50],
    pub padding2: [u64; 6],
    pub replace_buy_client_id: [u64; MAX_ORDER_LIMIT],
    pub replace_sell_client_id: [u64; MAX_ORDER_LIMIT],
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
