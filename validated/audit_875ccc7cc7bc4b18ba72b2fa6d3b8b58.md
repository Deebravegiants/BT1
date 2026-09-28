### Title
`require_external_recipient` rejects only the pool and controller, so `borrow`/`withdraw` can permanently strand tokens on other protocol contracts - (File: contracts/controller/src/positions/mod.rs)

### Summary
The Jackson bug class is a denylist that names a fixed set of "unsafe" values while accepting everything else unconditionally — `java.lang.Comparable` was omitted even though it was as broad and dangerous as the listed types. The lending analog is `require_external_recipient`, the recipient denylist applied to the `to: Option<Address>` argument of `borrow` and `withdraw`. It rejects exactly two protocol addresses — the controller and the pool — and unconditionally accepts every other protocol contract (position-nft, governance, price-aggregator, swap-aggregator, the configured accumulator). Tokens sent to the position-nft contract are permanently unrecoverable because that contract exposes no token-moving entrypoint, while the pool-side accounting (burned supply shares / minted debt shares and debited cash) has already been applied.

### Finding Description
`require_external_recipient` in `contracts/controller/src/positions/mod.rs:36-43` enforces:

```rust
assert_with_error!(
    env,
    *recipient != env.current_contract_address() && *recipient != pool,
    FlashLoanError::InvalidFlashloanReceiver
);
```

The in-code rationale (`positions/mod.rs:33-35`) and the regression test (`tests/test-harness/tests/controller/recipient_is_protocol_contract.rs:1-5`) explain why the two entries exist: a pool self-transfer debits `cash` without moving tokens, and controller-held funds can never be claimed by balance-delta accounting. Both are "unsafe base types" in the denylist's sense — protocol addresses where a token transfer permanently decouples book accounting from custody.

The list is incomplete. The position-nft contract's entire token-adjacent surface is `transfer`, `transfer_from`, `approve`, `approve_for_all` over NFT ids (`docs/reference/endpoints.md:244-247`); it has no `sweep`, no token `transfer`, and no generic invocation. The governance, price-aggregator, and swap-aggregator contracts likewise expose no entrypoint that moves an arbitrary token to an arbitrary recipient (`docs/reference/endpoints.md:259-330`). Yet `borrow(account, id, legs, Some(position_nft_address))` and `withdraw(account, id, legs, Some(position_nft_address))` pass the denylist and the pool executes `token.transfer(pool, position_nft, amount)`: the supply shares are burned and cash is debited, or debt shares are minted against live collateral, while the underlying tokens sit on a contract that can never move them.

### Impact Explanation
A `withdraw` addressed to the position-nft (or governance/aggregator/router) contract permanently burns the user's collateral value: shares are destroyed, `cash` is debited, and the tokens are frozen forever with no recovery entrypoint. A `borrow` is worse than a burn: the account keeps the minted debt obligation while the proceeds are frozen, so the position immediately carries the full liability with none of the funds, worsening its health factor toward liquidation. This is permanent freezing of user funds reachable by a single unprivileged call.

### Likelihood Explanation
Severity Medium: exploitation requires the caller (or a front-end/integration constructing the call on their behalf) to pass a protocol contract as `to`. Like the Jackson case, the vulnerable configuration is plausible rather than forced — copy-paste of a well-known deployment address (NFT, governance, router) as a recipient, or a buggy SDK default. When it occurs, the loss is total for the affected amount and there is no admin or upgrade-free recovery path. No external manipulation is needed.

### Recommendation
Extend `require_external_recipient` to reject every protocol-owned custody-less address: position-nft, governance, price-aggregator, swap-aggregator, and the configured revenue accumulator, in addition to the controller and pool. These are all resolvable from `Context`/`config` storage at call time. Alternatively, invert the model: require the recipient to differ from a stored set of protocol addresses, or require recipients to be the caller or an account/contract the caller explicitly designates off a denylist that enumerates all deployed module contracts.

### Proof of Concept
1. Admin deploys the protocol; note `nft_addr` = position-nft contract and `pool` = pool.
2. Alice calls `supply(alice, 0, [(hub,USDC), 10_000])`, creating account `id`.
3. Alice calls `withdraw(alice, id, [(hub,USDC), 10_000], Some(nft_addr))`.
4. `require_external_recipient` checks only `nft_addr != controller && nft_addr != pool` (`positions/mod.rs:38-42`) and passes.
5. The pool burns her scaled supply, debits `cash`, and executes `token.transfer(pool, nft_addr, 10_000 USDC)`.
6. Result: `balance(nft_addr) = 10_000 USDC` with no reachable entrypoint to move it; Alice's supply position is gone. Identical outcome via `borrow(..., Some(nft_addr))`, which additionally leaves her account holding the new debt shares.