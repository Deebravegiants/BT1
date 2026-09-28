### Title
`withdraw`/`borrow` `to` recipient is only screened against the pool and controller, so payouts can be directed to unrecoverable contract or dead addresses, permanently losing the funds - (File: contracts/controller/src/positions/mod.rs)

### Summary
The original report's bug class is a missing recipient check on the `to` field of a transfer, letting tokens be sent to an unrecoverable address and burned. XOXNO Lending exposes the same shape through the user-controlled `to: Option<Address>` on `Controller::withdraw` and `Controller::borrow`. The only guard, `require_external_recipient` in `contracts/controller/src/positions/mod.rs:36-43`, rejects just two addresses — the controller itself and the cached pool address. Any other `Address`, including protocol contracts that have no path to move tokens (e.g. the position-nft contract, the price-aggregator, an arbitrary dead contract, or a contract whose SAC balance no one can authorize), is accepted, and the pool then executes a real `token::Client::transfer` to it.

### Finding Description
`process_withdraw` resolves `to` into `recipient` and calls `require_external_recipient` before `settle_withdraw` sends the batch to `pool.withdraw(receiver, ...)` (`contracts/controller/src/positions/supply.rs:152-157`). The pool pays out via `Cache::transfer_out`, which performs `tok.transfer(&env.current_contract_address(), recipient, &amount)` with no destination validation (`contracts/pool/src/cache/cash.rs:46-52`). `process_borrow` follows the identical pattern: the recipient is checked only against the controller and the pool, then `pool.borrow(receiver, entries)` transfers borrowed tokens to it (`contracts/controller/src/positions/debt.rs:45-57`, `contracts/pool/README.md:106-107`). The check exists because a GH-17 fix recognized that protocol-owned recipients strand tokens — pool self-transfers debit `cash` without moving the balance, and controller-held funds are never claimed by balance-delta accounting (`contracts/controller/src/positions/mod.rs:33-35`, `tests/test-harness/tests/controller/recipient_is_protocol_contract.rs:1-5`) — but the fix enumerated only two of the protocol's contract addresses. On Soroban, SAC balances for contract addresses exist without any trustline requirement, so a transfer to the position-nft contract, the governance contract, the price-aggregator, or any arbitrary contract address succeeds and the tokens sit there with no withdrawal entrypoint. For account addresses the transfer fails closed if the account/trustline is missing, but a funded-but-uncontrolled account (e.g. an all-zero / keyless account id) succeeds and is equally unrecoverable.

### Impact Explanation
Permanent freezing/burning of funds: assets paid out by `withdraw` (the user's own collateral redemption) or `borrow` are transferred to an address that can never move them. Unlike EVM, there is no zero-address burn address, but an uncontrolled contract or dead account address is functionally identical — the tokens are removed from circulation with no recovery path, matching the report's "tokens sent to the zero address are effectively burned" impact.

### Likelihood Explanation
Any unprivileged account owner or delegate reaches this via a single call: `withdraw(caller, account_id, withdrawals, Some(dead_addr))` or `borrow(caller, account_id, borrows, Some(dead_addr))`. No privilege, timing, or external dependency is needed; the guard passes because `dead_addr` is neither the controller nor the pool. It is user-error-driven rather than attacker-driven, which is why it maps to the same Medium severity as the source report rather than Critical/High — the loss is limited to the funds the caller directs.

### Recommendation
Extend `require_external_recipient` to a denylist/allowlist that covers every protocol-owned contract address the controller knows (position-nft, governance, price-aggregator, swap venues used by strategies), or — stronger — only permit the recipient to be `caller` or a registered account owner address. At minimum, reject `Address` values that are contracts other than an explicit allowlist, since a contract recipient cannot authorize SAC spending of a stranded balance.

### Proof of Concept
```rust
// Harness-style test sketch (see tests/test-harness/tests/controller/
// recipient_is_protocol_contract.rs for the existing pool/controller cases).
#[test]
fn withdraw_to_unrecoverable_contract_strands_funds() {
    let mut t = LendingTest::new().standard_two_asset_dust_disabled();
    t.supply(ALICE, "USDC", 10_000.0);
    let id = t.account_id(ALICE);
    let alice = t.get_or_create_user(ALICE);

    // Any contract address that is neither the controller nor the pool:
    // e.g. the position-nft or price-aggregator contract, or a freshly
    // registered contract with no token-moving entrypoint.
    let dead_contract = t.env.register(
        soroban_sdk::testutils::MockContract, // any contract w/o transfer fn
        (),
    );

    let leg = vec![&t.env, (hub_asset(t.resolve_asset("USDC")), 10_000_000)];
    // Passes require_external_recipient: dead_contract != controller, != pool.
    t.ctrl_client().withdraw(&alice, &id, &leg, &Some(dead_contract.clone()));

    // Pool executed token::Client::transfer to dead_contract (cash.rs:46-52).
    // dead_contract has no entrypoint to move or authorize the balance;
    // the USDC is permanently frozen — the on-chain analog of a zero-address burn.
    assert_eq!(
        token::Client::new(&t.env, &t.resolve_asset("USDC")).balance(&dead_contract),
        10_000_000
    );
}
```

Relevant code: `require_external_recipient` — `contracts/controller/src/positions/mod.rs:36-43`; recipient resolution — `contracts/controller/src/positions/supply.rs:152-157` and `contracts/controller/src/positions/debt.rs:45-57`; unconditional payout — `contracts/pool/src/cache/cash.rs:46-52` and `contracts/pool/src/ops/withdraw.rs:48`.