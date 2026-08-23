No vulnerability found for this question.

The reported bug is a share-price inflation/donation attack specific to an ERC-20-style vault that mints shares (`rsETH`) as `totalAssetValue / totalSupply`, where `totalAssetValue` can be directly inflated by an attacker donating tokens to the pool contract. This pattern requires: (1) a pool contract that tracks value via `balanceOf` on itself/sub-contracts rather than internal accounting, and (2) a share-minting formula that divides by a totalSupply that can be pushed near zero.

nearcore has no such mechanism reachable from an unprivileged transaction. Token issuance in nearcore is a fixed, protocol-computed per-epoch inflation formula independent of any user-donatable balance — `epoch_total_reward = max_inflation_rate.numer * total_supply * epoch_duration / (...)`, entirely determined by `RewardCalculator::calculate_reward` [1](#0-0) , and `new_total_supply = prev.total_supply + minted_amount − balance_burnt` [2](#0-1) . There is no user-facing "deposit pool" whose valuation is computed from `balanceOf`-style external donations divided by a mintable share supply; account balances (`amount`/`locked`) are direct ledger entries, not shares in a pool [3](#0-2) . Storage staking similarly uses a fixed per-byte cost (`storage_amount_per_byte * storage_usage()`) rather than any share-price ratio [4](#0-3) .

Since nearcore itself does not implement a share/vault-style minting formula vulnerable to first-depositor donation manipulation in any unprivileged transaction/receipt/storage-staking/gas-metering path, this bug class does not have a reachable, concrete analog in the codebase (any such vault logic would exist only in a smart contract deployed *on* NEAR, which is out of scope for the core protocol).

### Citations

**File:** chain/epoch-manager/src/reward_calculator.rs (L51-51)
```rust
    pub fn calculate_reward(
```

**File:** core/primitives/src/block.rs (L193-193)
```rust
        .unwrap();
```

**File:** docs/ChainSpec/EpochAndStaking/Staking.md (L5-7)
```markdown
`Account` has two fields representing its tokens: `amount` and `locked`. `amount + locked` is the total number of
tokens an account has: locking/unlocking actions involve transferring balance between the two fields, and slashing
is done by subtracting from the `locked` value.
```

**File:** runtime/runtime/src/verifier.rs (L48-54)
```rust
    account: &Account,
    account_balance: Balance,
    runtime_config: &RuntimeConfig,
) -> Result<(), StorageStakingError> {
    let billable_storage_bytes = account.storage_usage();
    let required_amount = runtime_config
        .storage_amount_per_byte()
```
