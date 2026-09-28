[1](#0-0) ### Title
Unrestricted flash receiver can execute malicious code under the caller’s authorization tree - ([File: contracts/controller/src/strategies/flash_loan.rs])

### Summary
`flash_loan` accepts a caller-controlled `receiver` and opaque `data`, authenticates `caller`, and delegates execution to the pool. [2](#0-1) [3](#0-2)  The pool then invokes `execute_flash_loan` on that arbitrary contract and supplies the victim as `initiator`. [4](#0-3) [5](#0-4)  `flash_position` has the same attacker-controlled callback surface through `execute_flash_position`. [6](#0-5) [7](#0-6) 

### Finding Description
The receiver is analogous to the malicious dependency specification in the reported command injection: the protocol executes attacker-selected code from user-supplied input. A malicious receiver can use its `initiator` argument as the `from` address in calls to unrelated token contracts, causing those authorization requests to be attached beneath the caller’s authorized `flash_loan` or `flash_position` invocation.  The protocol checks only that `receiver` is a Wasm contract and that flash settlement succeeds; it does not constrain what additional caller-authorized calls the receiver makes. [3](#0-2) [4](#0-3) 

### Impact Explanation
If the victim signs the authorization tree returned by simulation, the receiver can transfer unrelated tokens or invoke other caller-authorized operations while still satisfying normal flash-loan repayment. This permits theft of user funds beyond the loan amount. [8](#0-7) 

### Likelihood Explanation
Exploitation requires the victim to select the malicious receiver and sign the expanded authorization tree, but no privileged protocol role or compromised key is needed. This matches the external report’s trust boundary where a victim executes an attacker-supplied artifact. [2](#0-1) 

### Recommendation
Restrict flash receivers to protocol-approved addresses or receiver code hashes, or require callers to use a protocol-owned callback dispatcher that cannot perform unrelated caller-authorized calls. Clients should also simulate and reject any signed authorization tree containing children other than the expected protocol operations. [9](#0-8) 

### Proof of Concept
1. The victim calls `flash_loan(caller = victim, asset = listed_asset, amount = loan, receiver = malicious_contract, data = arbitrary)`. [2](#0-1) 
2. The pool sends `loan` to `malicious_contract` and invokes `execute_flash_loan(initiator = victim, ..., data)`. [10](#0-9) [5](#0-4) 
3. The receiver calls an unrelated token’s `transfer(victim, attacker, victim_balance)` and approves `amount + fee` for repayment. 
4. Simulation records the token transfer as a child of the victim’s `flash_loan` authorization; if the victim signs that tree, the transfer and the flash-loan settlement both execute.

### Citations

**File:** contracts/controller/src/lib.rs (L171-179)
```rust
    fn flash_loan(
        env: Env,
        caller: Address,
        asset: HubAssetKey,
        amount: i128,
        receiver: Address,
        data: Bytes,
    ) {
        strategies::flash_loan::process_flash_loan(&env, &caller, &asset, amount, &receiver, &data);
```

**File:** contracts/controller/src/lib.rs (L189-201)
```rust
    fn flash_position(
        env: Env,
        caller: Address,
        account_id: u64,
        spoke_id: u32,
        mode: PositionMode,
        debt: HubAssetKey,
        amount: i128,
        receiver: Address,
        data: Bytes,
        collaterals: Vec<(HubAssetKey, i128)>,
        refund_assets: Vec<Address>,
    ) -> u64 {
```

**File:** contracts/controller/src/strategies/flash_loan.rs (L22-32)
```rust
    require_authorized_caller(env, caller);
    require_positive_amount(env, amount);
    config::require_hub_active(env, hub_asset.hub_id);

    require_wasm_receiver(env, receiver);

    let mut cache = Context::new(env);
    let pool_addr = cache.cached_pool_address();

    let fee = storage::with_flash_guard(env, || {
        pool_flash_loan_call(env, &pool_addr, hub_asset, caller, receiver, amount, data)
```

**File:** contracts/pool/src/ops/flash.rs (L60-67)
```rust
    asset.transfer(&pool, &receiver, &amount);
    require_balance(env, &asset, &pool, terms.balance_after_payout);
    invoke_receiver(
        env, &cache, &receiver, initiator, amount, terms.fee, &pool, data,
    );

    require_balance(env, &asset, &pool, terms.balance_after_payout);
    collect_repayment(env, &asset, &pool, &receiver, &terms);
```

**File:** contracts/pool/src/ops/flash.rs (L150-162)
```rust
    env.invoke_contract::<()>(
        receiver,
        &Symbol::new(env, "execute_flash_loan"),
        (
            initiator,
            cache.params().asset_id.clone(),
            amount,
            fee,
            pool.clone(),
            data,
        )
            .into_val(env),
    );
```

**File:** contracts/controller/src/strategies/flash_position.rs (L308-321)
```rust
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
```
