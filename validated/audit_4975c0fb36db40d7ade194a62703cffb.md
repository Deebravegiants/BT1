### Title
Unprivileged caller-supplied `receiver` contract inherits controller invoker auth during `flash_position` callback, enabling privileged calls into the pool contract - (File: contracts/controller/src/strategies/flash_position.rs)

### Summary
`process_flash_position` invokes an entirely attacker-chosen contract address (`receiver`) via `env.invoke_contract` while the call executes under the controller's invoker-contract authority. The flash guard (`storage::with_flash_guard`) only blocks reentry into the controller's own monetary entrypoints; it does not prevent the receiver from making sub-invocations to *other* contracts (the pool, listed tokens) that carry the controller's invoker auth. This is the on-chain analog of CVE-2018-6871's attacker-controlled `=WEBSERVICE` target: a user-supplied "formula" (the `receiver` address) causes the trusted component to reach out to and act upon arbitrary external resources with its own authority.

### Finding Description
In `contracts/controller/src/strategies/flash_position.rs`, `process_flash_position` validates only that `receiver` is a WASM contract (`require_wasm_receiver`), is not the controller, and is not the pool itself (lines 69–84). There is no allowlist for `receiver`. It then calls `invoke_receiver` (lines 297–323), which performs `env.invoke_contract(receiver, "execute_flash_position", ...)` inside `with_flash_guard` (lines 120–143).

Under Soroban invoker-contract auth, any contract called by the controller can itself perform sub-invocations that require the *controller's* authorization. The flash guard is implemented in the controller's own storage (`storage::with_flash_guard`), so it only gates functions that check that flag — i.e., controller monetary entrypoints. The pool contract is a separate contract with separate storage; a malicious `receiver` contract can, during the callback, directly invoke pool entrypoints (e.g., borrow/release liquidity paths) with the controller's invoker auth attached, bypassing every controller-side check: no position bookkeeping, no collateral requirement, no `is_flashloanable` gate beyond the initial one, no risk gates (`strategy_finalize` gates only the attacker's own account, which is irrelevant if funds were pulled straight from the pool).

Notably, `receiver != pool_addr` is checked (lines 80–84) but that only prevents the pool being the *callback target* — it does nothing to stop the receiver contract from calling the pool as a sub-invocation.

### Impact Explanation
If any pool entrypoint that moves funds (debt disbursement, supply withdrawal, share operations) authorizes via `controller.require_auth()` / equivalent invoker auth rather than an immediate-invoker check, a malicious receiver contract drains pool liquidity during the callback with no debt recorded against any account — direct theft of supplier funds / protocol insolvency. Even where the pool is hardened, the same primitive lets the receiver invoke any third-party contract (e.g., a listed token SAC's admin functions, or the position NFT contract) under the controller's authority.

### Likelihood Explanation
Fully reachable by any unprivileged address: `flash_position` requires only `require_authorized_caller`, an active hub, and `is_flashloanable` on the chosen debt market. The attacker deploys a WASM contract implementing `execute_flash_position`, passes it as `receiver`, and performs the privileged sub-invocation inside the callback. Cost is minimal (dust collateral plus the flash borrow, which is fee-free per `fee: 0` at line 164). The residual uncertainty is the pool's exact auth primitive (`require_auth` on the controller address vs. an immediate-invoker check); the codebase context I could retrieve did not show the pool's auth implementation directly, so confirmation requires reading the pool's authorization checks — this is the one point I could not fully verify within the index.

### Recommendation
Do not expose raw invoker auth to an untrusted callee. Options, in order of preference:
1. Change the pool (and any contract that trusts the controller) to verify the *immediate invoker* rather than relying on `require_auth` against the controller address, so transitive callbacks cannot impersonate it.
2. Or restrict `receiver` in `flash_position`/`flash_loan` to a governance-managed allowlist (mirroring `INV-STRAT-03`'s approved-pool model for Blend migration).
3. At minimum, extend the guard scope: set a flag that the pool checks before executing any state-changing call, or perform `invoke_receiver` outside a context where controller-authorized sub-invocations are possible (Soroban does not offer selective auth stripping, so option 1 or 2 is the real fix).

### Proof of Concept
1. Attacker deploys `Evil` contract with an `execute_flash_position(initiator, account_id, asset, amount, fee, amount_received, controller, data)` entrypoint that, when invoked, calls `pool.<fund-moving-entrypoint>(args…)` — the sub-invocation carries the controller's invoker auth.
2. Attacker calls `controller.flash_position(caller=attacker, debt=(hub, USDC), amount=X, receiver=Evil, collaterals=[(any listed asset, min=1)], refund_assets=[], data=…)`.
3. `mint_and_forward` mints fee-free debt to the controller and forwards to `Evil`; `invoke_receiver` then calls `Evil.execute_flash_position` inside `with_flash_guard` — the guard blocks controller reentry but not `Evil → pool`.
4. `Evil` sub-invokes the pool's fund-moving function as the controller, extracting tokens beyond the flash-minted amount, then returns normally; collateral minimums and final risk checks apply only to the attacker's account and pass trivially. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/controller/src/strategies/flash_position.rs (L69-91)
```rust
    require_wasm_receiver(env, receiver);

    let controller = env.current_contract_address();
    assert_with_error!(
        env,
        *receiver != controller,
        FlashLoanError::InvalidFlashloanReceiver
    );

    let mut cache = Context::new(env);
    let pool_addr = cache.cached_pool_address();
    assert_with_error!(
        env,
        *receiver != pool_addr,
        FlashLoanError::InvalidFlashloanReceiver
    );
    // Caller-selected receivers require flash loans enabled; multiply uses
    // the configured router and does not require this flag.
    assert_with_error!(
        env,
        cache.cached_pool_sync_data(debt).params.is_flashloanable,
        FlashLoanError::FlashloanNotEnabled
    );
```

**File:** contracts/controller/src/strategies/flash_position.rs (L119-143)
```rust
    // Guard both forwarding and the callback: token hooks can reenter first.
    let (amount_received, collateral_before, refund_before) =
        storage::with_flash_guard(env, || {
            let amount_received =
                mint_and_forward(env, &mut account, debt, amount, receiver, &mut cache);
            // Baselines exclude funding and forwarding; count callback receipts only.
            let collateral_before = snapshot_balances(
                env,
                &controller,
                collaterals.iter().map(|(hub_asset, _)| hub_asset.asset),
            );
            let refund_before = snapshot_balances(env, &controller, refund_assets.iter());
            invoke_receiver(
                env,
                receiver,
                caller,
                account_id,
                &debt.asset,
                amount,
                amount_received,
                &controller,
                data,
            );
            (amount_received, collateral_before, refund_before)
        });
```

**File:** contracts/controller/src/strategies/flash_position.rs (L297-323)
```rust
fn invoke_receiver(
    env: &Env,
    receiver: &Address,
    initiator: &Address,
    account_id: u64,
    asset: &Address,
    amount: i128,
    amount_received: i128,
    controller: &Address,
    data: &Bytes,
) {
    env.invoke_contract::<()>(
        receiver,
        &Symbol::new(env, "execute_flash_position"),
        (
            initiator.clone(),
            account_id,
            asset.clone(),
            amount,
            0i128,
            amount_received,
            controller.clone(),
            data.clone(),
        )
            .into_val(env),
    );
}
```
