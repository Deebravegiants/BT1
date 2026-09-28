### Title
A contract can receive a position NFT it cannot operate, permanently locking the lending account’s funds - (File: contracts/position-nft/src/contract.rs)

### Summary
Severity: Medium. Account-creating controller calls mint the position NFT directly to the authorizing `caller` without checking whether that address can later authorize NFT or controller operations. If the caller is a contract without a controller/NFT management path, the position and its collateral can become permanently inaccessible. [1](#0-0) [2](#0-1) 

### Finding Description
`supply` requires `caller` authorization, treats `account_id = 0` as account creation, and passes `caller` as the account owner. [3](#0-2) 

`create_account_with` forwards that owner to `nft_mint_call`, while `PositionNft::mint` unconditionally calls `Enumerable::sequential_mint(e, &to)`. [4](#0-3) [2](#0-1) 

Neither the mint nor the ordinary transfer path verifies that `to` is an externally owned account or that a contract recipient exposes functions capable of authorizing `transfer`, `approve`, or controller account operations. [5](#0-4) 

NFT ownership is the live authority over the entire lending account, including its collateral and debt. [6](#0-5) 

Consequently, a contract that receives a position NFT but has no callable path to authorize `transfer`, `approve`, `approve_for_all`, or `withdraw` permanently owns an account it cannot operate. [7](#0-6) [8](#0-7) 

### Impact Explanation
All supplied collateral represented by the affected account can remain locked in the pool indefinitely. The owner cannot withdraw or transfer the position unless the recipient contract already exposes an authorization path; ordinary external callers cannot produce the contract address’s authorization. [8](#0-7) [9](#0-8) 

This is permanent freezing of user funds rather than a transient denial of service: the NFT exists, the account remains solvent, and the accounting remains valid, but no reachable authorization can move the collateral. [10](#0-9) 

### Likelihood Explanation
Contract-owned positions are a supported shape rather than an edge case: account ID `0` can create an account through `supply`, `multiply`, `flash_position`, `migrate_from_blend`, or liquidation `Credit(0)`. [11](#0-10) 

An integrating contract only needs to call one of those entrypoints while omitting a later NFT-management or withdrawal method to trigger the condition. The same freeze can also occur when a user transfers an existing NFT to a contract that cannot authorize subsequent actions. [12](#0-11) [9](#0-8) 

### Recommendation
Introduce a safe-mint analogue for account creation: require a contract recipient to complete a protocol-defined ownership acknowledgement that proves it can authorize position-NFT operations, or reject contract callers if contract-owned accounts are not intended. Apply the same explicit receiver policy to documented contract-account flows such as `supply`, `multiply`, `flash_position`, `migrate_from_blend`, and `Credit(0)` liquidation receivers. [2](#0-1) [11](#0-10) 

At minimum, document and test a mandatory contract-account interface covering `transfer`, `approve`, `withdraw`, `add_delegate`, and account renewal so integrations cannot accidentally create inaccessible positions. [5](#0-4) [13](#0-12) 

### Proof of Concept
1. Deploy `LockedStrategy`, a contract exposing only a `deposit` function and no function that calls the position NFT or controller withdrawal entrypoints.
2. Fund `LockedStrategy` with a listed asset.
3. `LockedStrategy.deposit` invokes:

```rust
controller.supply(
    locked_strategy_address, // caller and future owner
    0,                       // create account
    spoke_id,
    assets,                  // positive measured payment
);
```

4. `process_supply` authorizes the contract caller, `load_or_create_account` creates the account, and `PositionNft::mint` assigns the token to `locked_strategy_address`. [1](#0-0) [2](#0-1) 
5. `owner_of(account_id)` now returns `locked_strategy_address`, and that NFT controls the collateral. [14](#0-13) 
6. Calling `position_nft.transfer(locked_strategy_address, recipient, account_id)` fails because no transaction signer can produce the contract’s authorization and the contract exposes no function to invoke the transfer itself. [9](#0-8) 
7. Calling `controller.withdraw(locked_strategy_address, account_id, ...)` likewise fails the owner/delegate check, leaving the deposited collateral locked while both the NFT and account remain live. [8](#0-7)

### Citations

**File:** contracts/controller/src/positions/supply.rs (L47-63)
```rust
    validation::require_authorized_caller(env, caller);
    let aggregated = payments::aggregate_positive_payments(env, assets);
    let mut cache = Context::new(env);

    let (acct_id, mut account) = account::load_or_create_account(
        env,
        caller,
        account_id,
        spoke_id,
        PositionMode::Normal,
        account::AccountGuard::Supply,
        &mut cache,
    );

    require_third_party_existing_supply(env, account_id, acct_id, caller, &account, &aggregated);

    process_deposit(env, caller, &mut account, &aggregated, &mut cache);
```

**File:** contracts/controller/src/positions/supply.rs (L147-157)
```rust
    validation::require_authorized_caller(env, caller);

    let mut account = storage::get_account(env, account_id);
    require_owner_or_delegate(env, account_id, caller, &account.owner);

    let recipient = to.unwrap_or_else(|| caller.clone());
    let mut cache = Context::new(env);
    require_external_recipient(env, &mut cache, &recipient);
    let aggregated = payments::aggregate_payments(env, withdrawals, payments::ZeroLeg::MeansAll);

    let paid = settle_withdraw(env, &mut account, &recipient, &aggregated, &mut cache);
```

**File:** contracts/position-nft/src/contract.rs (L68-75)
```rust
    pub fn mint(e: &Env, to: Address) -> u32 {
        controller(e).require_auth();
        renew_instance(e);
        let token_id = Enumerable::sequential_mint(e, &to);
        // sequential_mint writes Owner/Balance at the network minimum TTL; lift
        // them to the user window so a new position does not archive early.
        extend_user_persistent_ttl(e, &to, token_id);
        token_id
```

**File:** contracts/controller/src/account.rs (L62-71)
```rust
    let nft = storage::get_position_nft(env);
    let account_id = nft_mint_call(env, &nft, owner);
    let account = Account {
        owner: owner.clone(),
        spoke_id,
        mode,
        supply_positions: Map::new(env),
        borrow_positions: Map::new(env),
    };
    storage::set_account_meta(env, account_id, &AccountMeta { spoke_id, mode });
```

**File:** contracts/controller/src/account.rs (L83-97)
```rust
/// Creates an account for `caller` when `account_id` is zero; otherwise loads it.
/// Existing accounts require a matching spoke. `Migrate` also requires an owner
/// or active delegate; `Multiply` additionally requires a matching mode.
pub(crate) fn load_or_create_account(
    env: &Env,
    caller: &Address,
    account_id: u64,
    spoke_id: u32,
    mode: PositionMode,
    guard: AccountGuard,
    cache: &mut Context,
) -> (u64, Account) {
    if account_id == 0 {
        return create_account(env, caller, spoke_id, mode, cache);
    }
```

**File:** contracts/position-nft/README.md (L29-41)
```markdown
| any owner check (`try_account_owner`) | `owner_of(token_id)` | Live lookup; the owner is never cached in controller storage |
| `renew_account` | `renew(token_id)` | Lifts the token's `Owner` entry and its holder's `Balance` entry to the protocol's per-user window |
| `upgrade_position_nft` | `upgrade(hash)` | Owner-gated Wasm upgrade |

`account_id == token_id`. The controller widens `u32` to `u64` on mint and
narrows back with `u32::try_from` on every other call; an id above `u32::MAX`
can never have been minted, so it resolves to `AccountNotFound`. Account id `0`
is the controller's "create a new account" sentinel, so the constructor
consumes token id 0 and the first real position is id 1.

Transferring the token transfers the whole position. Nothing in the controller
changes on transfer: the next controller call resolves the new holder and
accepts it. Collateral and debt both move with the token.
```

**File:** contracts/position-nft/README.md (L60-65)
```markdown
| `balance` | `fn balance(e: &Env, account: Address) -> u32` | Anyone | Number of positions held by `account` |
| `owner_of` | `fn owner_of(e: &Env, token_id: u32) -> Address` | Anyone | Current holder; panics `NonExistentToken` if never minted or burned |
| `transfer` | `fn transfer(e: &Env, from: Address, to: Address, token_id: u32)` | `from` must authorize | Moves the position to `to` |
| `transfer_from` | `fn transfer_from(e: &Env, spender: Address, from: Address, to: Address, token_id: u32)` | `spender` must authorize and be `from`, approved for the token, or an operator for `from` | Moves the position to `to` |
| `approve` | `fn approve(e: &Env, approver: Address, approved: Address, token_id: u32, live_until_ledger: u32)` | `approver` must authorize and be the owner or an operator | Grants `approved` the right to move that one position until `live_until_ledger` |
| `approve_for_all` | `fn approve_for_all(e: &Env, owner: Address, operator: Address, live_until_ledger: u32)` | `owner` must authorize | Makes `operator` able to move every position `owner` holds until `live_until_ledger`; `0` revokes |
```

**File:** docs/explanation/threat-model.md (L75-93)
```markdown
## Account authority

The position NFT holder controls the lending account. Approving an NFT
operator enables transfer of the entire position, including collateral and
debt. This is not a narrowly scoped permission to handle a collectible.

An account delegate also needs active global position-manager registration.
Its grant is stamped with the granting owner's address, not a transfer epoch:
it becomes inactive while someone else holds the NFT and can revive if the
NFT returns before an intervening owner updates delegates. Owner revocation
is immediate; global deactivation takes effect when governance executes it.
Delegates can borrow/withdraw to their chosen recipient within account gates.
Those gates do not constrain them to acting in the owner's economic interest.

Controller account renewal requires the owner. Direct NFT renewal is
permissionless and extends the Owner entry, its holder's Balance entry, and
instance time to live (TTL); it does not renew the controller account. Archived
persistent entries need restoration. Sequential NFT IDs are finite and are not
recycled. Renewal and position limits do not guarantee that maximum-size
```

**File:** skills/xoxno-lending-contracts/positions.md (L7-18)
```markdown
## Lifecycle

- ID `0` creates an account through `supply`, `multiply`, `flash_position`,
  `migrate_from_blend`, or liquidation `Credit(0)`. Store the returned ID.
- `account_exists(id)` checks and renews only the controller's
  `AccountMeta(id)`. It does not renew or prove the existence of position maps,
  delegates, NFT entries, your local pointer, or your contract instance.
- Cleanup depends on the operation. `withdraw` and the strategy verbs remove
  the account when both position maps end empty. Liquidation and
  `clean_bad_debt` remove it through their own paths. `repay` writes only the
  debt side and does not remove an empty account.
- Deletion removes controller entries and burns the NFT atomically. IDs are
```
