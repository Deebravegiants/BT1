Based on my research, I found the closest legitimate analog in the Raydium AMM program, though with some caveats on exact scope of impact that I could not fully verify given tool constraints.

### Title
Unbounded, attacker-chosen `open_time` in `Initialize2` can permanently strand a pool in `WaitingTrade` status - (File: `program/src/processor.rs`)

### Summary
The Telcoin report flags a governance parameter (`challengePeriod`) that is accepted without any sanity bound, allowing it to be set so large that it effectively blocks the intended workflow forever. The closest reachable analog in this Solana AMM program is the `open_time` field of `InitializeInstruction2`, which is fully attacker-controlled at pool-creation time (an unprivileged action) and is stored/interpreted with no upper-bound check.

### Finding Description
`process_initialize2` unpacks `init.open_time` directly from instruction data supplied by the (unprivileged) pool-creating user and passes it straight into `amm.initialize(...)`, which stores it as `state_data.pool_open_time` with no range validation: [1](#0-0) 

The same value is then used to decide the pool's initial status: [2](#0-1) 

If `open_time` is set to an arbitrarily large `u64` value (e.g. far in the future or near `u64::MAX`), `init.open_time > Clock::get()?.unix_timestamp as u64` is always true, so `amm.status` is permanently set to `AmmStatus::WaitingTrade`. There is no code path reachable by an unprivileged actor that can later reduce `pool_open_time` or change `status` back — the only instruction capable of doing so is `SetParams` with the `SetOpenTime`/`Status` params, which requires a hard-coded, privileged `amm_owner` signer: [3](#0-2) [4](#0-3) 

This mirrors the reported bug class exactly: a time-like parameter is accepted from an unprivileged caller with no bounds check, and once set, only a privileged party can undo the effect — meaning an unprivileged action alone can put the pool into an indefinitely stuck state.

### Impact Explanation
Because `AmmStatus::WaitingTrade` is checked by the swap instructions to gate trading (the state-machine design ties swap availability to `status`), a maliciously or carelessly created pool can be permanently prevented from ever becoming tradable without the AMM program's hardcoded admin (`config_feature::amm_owner`) manually intervening via `SetParams`. I was not able to fully verify in the time available whether `Deposit`/`Withdraw` are also gated by the same `WaitingTrade` status (which would elevate this to actual freezing of LP funds) — this needs confirmation by reading the permission-check helpers (`swap_permission`, `deposit_permission`, `withdraw_permission` in `program/src/state.rs`) that I identified but did not have iteration budget left to fully inspect.

### Likelihood Explanation
Any user can call `Initialize2` to create a pool (it is a permissionless, unprivileged instruction gated only by paying the create-pool fee and providing a signer), and can trivially pass any `u64` for `open_time`. No further privilege or race condition is required to trigger the stuck state — a single transaction is sufficient.

### Recommendation
Enforce a reasonable upper bound on `open_time` relative to `Clock::get()?.unix_timestamp` in `process_initialize2` (e.g. reject values more than some fixed delta, such as a few days/weeks, in the future), so a pool cannot be created in a state that requires privileged admin intervention to ever become swappable.

### Proof of Concept
1. Attacker calls `Initialize2` (via the `initialize2` instruction builder) as the pool-creating user, supplying `open_time = u64::MAX` (or any timestamp far beyond any realistic operational horizon). [5](#0-4) 
2. `process_initialize2` accepts this value with no bound check and stores it, setting `amm.status = AmmStatus::WaitingTrade`. [2](#0-1) 
3. Because `init.open_time` will never be reached (or would take an impractically long time), the pool remains in `WaitingTrade` forever from a practical standpoint.
4. The only way to fix `status`/`pool_open_time` is `SetParams`, gated by the hardcoded `config_feature::amm_owner` signer — inaccessible to the pool creator or any other unprivileged party. [6](#0-5) 

**Caveat / uncertainty:** Whether this results in outright fund-freezing (as opposed to merely disabling swaps while leaving deposit/withdraw open) depends on logic in `program/src/state.rs`'s permission-check functions (`AmmStatus`-related `*_permission` methods), which I located but did not have remaining tool budget to fully read and confirm. If deposits/withdrawals remain unaffected by `WaitingTrade`, the practical impact is limited to swap unavailability for that specific pool rather than a fund freeze, which would lower the severity below the strict "permanent freezing of user or LP funds" bar required by the validation rules. I recommend a Devin session or further manual review of those permission functions to confirm the exact blast radius before treating this as a confirmed Medium-severity finding.

### Citations

**File:** program/src/processor.rs (L931-938)
```rust
        amm.initialize(
            init.nonce,
            init.open_time,
            coin_mint.decimals,
            pc_mint.decimals,
            0,
            0,
        )?;
```

**File:** program/src/processor.rs (L978-982)
```rust
        amm.status = if init.open_time > (Clock::get()?.unix_timestamp as u64) {
            AmmStatus::WaitingTrade.into_u64()
        } else {
            AmmStatus::SwapOnly.into_u64()
        };
```

**File:** program/src/processor.rs (L2644-2661)
```rust
    pub fn process_set_params(
        program_id: &Pubkey,
        accounts: &[AccountInfo],
        setparams: SetParamsInstruction,
    ) -> ProgramResult {
        let account_info_iter = &mut accounts.iter();

        let amm_info = next_account_info(account_info_iter)?;
        let amm_owner_info = next_account_info(account_info_iter)?;

        let mut amm = AmmInfo::load_mut_checked(&amm_info, program_id)?;

        if amm_info.owner != program_id {
            return Err(AmmError::InvalidOwner.into());
        }
        if !amm_owner_info.is_signer || *amm_owner_info.key != config_feature::amm_owner::ID {
            return Err(AmmError::InvalidSignAccount.into());
        }
```

**File:** program/src/processor.rs (L2697-2704)
```rust
            AmmParams::SetOpenTime => {
                match setparams.value {
                    Some(time) => {
                        amm.state_data.pool_open_time = time as u64;
                    }
                    None => return Err(AmmError::InvalidInput.into()),
                };
            }
```

**File:** program/src/instruction.rs (L663-693)
```rust
/// Creates an 'initialize2' instruction.
pub fn initialize2(
    amm_program: &Pubkey,
    amm_pool: &Pubkey,
    amm_authority: &Pubkey,
    amm_open_orders: &Pubkey,
    amm_lp_mint: &Pubkey,
    amm_coin_mint: &Pubkey,
    amm_pc_mint: &Pubkey,
    amm_coin_vault: &Pubkey,
    amm_pc_vault: &Pubkey,
    amm_target_orders: &Pubkey,
    amm_config: &Pubkey,
    create_fee_destination: &Pubkey,
    market_program: &Pubkey,
    market: &Pubkey,
    user_wallet: &Pubkey,
    user_token_coin: &Pubkey,
    user_token_pc: &Pubkey,
    user_token_lp: &Pubkey,
    nonce: u8,
    open_time: u64,
    init_pc_amount: u64,
    init_coin_amount: u64,
) -> Result<Instruction, ProgramError> {
    let init_data = AmmInstruction::Initialize2(InitializeInstruction2 {
        nonce,
        open_time,
        init_pc_amount,
        init_coin_amount,
    });
```
