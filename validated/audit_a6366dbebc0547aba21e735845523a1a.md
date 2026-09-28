### Title
Unbounded dust-account creation floods persistent storage and outruns the keeper's renewal window, forcing account archival and freezing of funds - (File: contracts/controller/src/positions/supply.rs)

### Summary
Any address can mint an unlimited number of new lending accounts by calling `supply` with `account_id = 0` and a 1-unit deposit. There is no minimum deposit, no per-owner account cap, and no fee beyond the deposit itself. Each call writes a permanent set of persistent entries (`AccountMeta`, `SupplyPositions`, `BorrowPositions`, NFT `Owner`/`Balance`/enumeration keys) keyed by a monotonically increasing id. This is the on-chain analog of the fake-stake disk-filling attack: a cheap, repeated action creates permanent ledger state that other actors' operations must coexist with, and in Soroban the cost of keeping that state alive falls on the protocol's TTL-renewal machinery rather than on the attacker.

### Finding Description
`process_supply` resolves `account_id == 0` through `load_or_create_account`, which calls `create_account` → `nft_mint_call` → `storage::set_account_meta`, minting a fresh sequential id for every call (`contracts/controller/src/account.rs:25-74`, `contracts/controller/src/positions/supply.rs:38-74`). `aggregate_positive_payments` accepts `amount = 1`; the regression test `poc_single_actor_spams_unbounded_dust_accounts` proves one actor can mint N accounts with N stroops-like units (`tests/test-harness/tests/controller/supply.rs:312-344`). `validate_bulk_position_limits` only bounds positions *within* an account (`contracts/controller/src/risk/validation.rs:63-112`); nothing bounds the number of accounts.

The account-id space is a dense sequential counter. The keeper discovers per-user keys (`AccountMeta`, `SupplyPositions`, `BorrowPositions`, `Delegates`, NFT `Owner`) by scanning ids `1..=max_account_id` in windows of at most `max_accounts_scan` (default 50,000) per TTL tick, wrapping around (`services/keeper/README.md:35-44`). Spamming the id space therefore:

- multiplies the number of persistent entries the keeper must renew each cycle (unbounded rent burden on the protocol's renewal budget), and
- stretches the full scan cycle to `ceil(max_account_id / 50000)` ticks, so real user entries sit un-renewed for proportionally longer.

Once a user entry's TTL lapses it archives; every controller call touching that account (`withdraw`, `borrow`, `repay`, `liquidate`, `renew_account` owner lookups via `owner_of`) fails until the entry is restored, which the threat model itself lists as a known availability cost (DoS.6). Position limits (`POSITION_LIMIT_MAX = 5`) and dust floors that constrain *within-account* state do not constrain the account dimension at all.

### Impact Explanation
Temporary freezing of user funds and permanent storage bloat. An attacker holding a trivial token balance can mint millions of dust accounts; each pushes the renewal scan further behind, increasing the probability that legitimate accounts' persistent entries archive between keeper visits, blocking withdrawals and liquidations until restoration. Even absent archival, the protocol's keeper must pay renewal fees for an ever-growing set of attacker-controlled entries — a sustained drain with no way to delete or refuse the spammed accounts (account deletion is owner-initiated via withdraw/burn).

### Likelihood Explanation
Cheap and permissionless: one `supply(0, spoke_id, [(asset, 1)])` call per account, no collateral quality required, no price/oracle dependency, no governance action. The only cost is the per-entry Soroban rent the attacker pays once — after which renewal burden shifts to the keeper. Requires no privileged role, no bug in pricing, and no cross-contract manipulation.

### Recommendation
Enforce a minimum initial deposit (a USD value via `min_borrow_collateral_usd`-style strict pricing, or a per-asset dust floor at account creation) so that each spammed account costs meaningful capital, and/or cap accounts per owner. Consider charging an explicit account-creation deposit that is only refundable on `remove_account`. Optionally, let anyone permissionlessly burn empty dust accounts (zero supply and zero debt) to reclaim the id space and keep the keeper scan dense.

### Proof of Concept
```rust
// tests/test-harness/tests/controller/supply.rs:312-344
#[test]
fn poc_single_actor_spams_unbounded_dust_accounts() {
    let mut t = LendingTest::new().with_market(usdc_preset()).build();
    let attacker = t.get_or_create_user("attacker");
    let usdc = t.resolve_market("USDC");

    const N: u64 = 64;
    usdc.token_admin.mint(&attacker, &(N as i128));
    let ctrl = t.ctrl_client();
    for _ in 0..N {
        let dust = vec![&t.env, (hub_asset(usdc.asset.clone()), 1i128)];
        let id = ctrl.supply(&attacker, &0u64, &1u32, &dust); // 1 unit, account_id=0
        assert!(id > 0 && ctrl.account_exists(&id));          // persists forever
    }
}
```
Scaling `N` to 50,000+ exhausts one keeper scan window (`max_accounts_scan` default); continued spam stretches the renewal cycle arbitrarily while each account's five-plus persistent keys accumulate on-ledger.