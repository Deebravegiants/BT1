### Title
Attacker-controlled flash-loan receiver can inject token transfers into the caller’s authorization tree - (File: contracts/pool/src/ops/flash.rs)

### Summary
`flash_loan` invokes a caller-selected contract while the original caller’s authorization remains active, and passes that caller’s address to the receiver as `initiator`. A malicious receiver can therefore construct an additional `token.transfer(initiator, attacker, amount)` call; simulation will include it beneath the caller’s `flash_loan` authorization, and signing that poisoned tree lets the receiver steal wallet assets unrelated to the loan. [1](#0-0) [2](#0-1) 

### Finding Description
The controller exposes `flash_loan(caller, asset, amount, receiver, data)` with `receiver` supplied directly by the caller and no receiver allowlist. [1](#0-0) 

The pool invokes the selected contract through `env.invoke_contract`, supplying both `initiator` and arbitrary callback `data`. [3](#0-2) 

Because `execute_flash_loan` is arbitrary Wasm, the receiver can use the supplied `initiator` as the `from` address of a token transfer to an attacker-controlled destination before approving the required `amount + fee` repayment. [3](#0-2) [4](#0-3) 

This is the Soroban analogue of command injection: attacker-controlled input selects the code that executes inside a privileged authorization context, and the injected code can add commands that were not part of the intended flash-loan operation. [5](#0-4) [3](#0-2) 

### Impact Explanation
A successful call steals arbitrary tokens held by the initiating wallet, including assets that are not listed by the lending protocol and assets unrelated to the borrowed amount. [3](#0-2) 

The malicious receiver can still approve `amount + fee`, so the pool’s repayment checks can succeed while the unrelated wallet-token theft remains part of the same committed transaction. [6](#0-5) 

### Likelihood Explanation
The attacker only needs to deploy a Wasm receiver and convince a borrower to use it as the `receiver` argument; no protocol privilege, leaked key, governance action, or oracle manipulation is required. [5](#0-4) 

Execution requires the victim to sign the authorization tree containing the injected child transfer, so the attack depends on wallet UX, opaque authorization display, or failure to inspect the simulation-generated tree. [3](#0-2) 

### Recommendation
Bind flash-loan receivers to an explicit allowlist or receiver registry approved through governance rather than accepting an arbitrary contract address. [5](#0-4) 

If arbitrary receivers remain supported, pass a dedicated authorization context or require an operation-specific signed payload so receiver execution cannot add unrelated calls beneath the caller’s root authorization. [3](#0-2) 

Clients should also simulate every flash loan, decode the complete authorization tree, and reject any child invocation other than the expected repayment approval or explicitly intended receiver operations. [6](#0-5) 

### Proof of Concept
Deploy a malicious receiver configured with the target wallet token, attacker destination, and amount:

```rust
pub fn execute_flash_loan(
    env: Env,
    initiator: Address,
    asset: Address,
    amount: i128,
    fee: i128,
    pool: Address,
    _data: Bytes,
) {
    let cfg = config(&env);

    // Injected command: spends an unrelated token held by the flash-loan caller.
    token::Client::new(&env, &cfg.wallet_token).transfer(
        &initiator,
        &cfg.attacker,
        &cfg.amount,
    );

    // Make the enclosing flash-loan settlement succeed.
    token::Client::new(&env, &asset).approve(
        &env.current_contract_address(),
        &pool,
        &(amount + fee),
        &env.ledger().sequence() + 1,
    );
}
```

The victim then calls `controller.flash_loan(victim, asset, amount, malicious_receiver, data)`. [5](#0-4) 

The pool reaches `invoke_receiver`, which invokes `execute_flash_loan` with `initiator = victim`; the malicious contract performs the unrelated transfer and then grants the repayment allowance expected by `collect_repayment`. [6](#0-5) 

If the victim signs the simulation-produced authorization tree containing that child transfer, the transaction completes with both the flash loan repayment and the attacker’s theft of the unrelated wallet token. [6](#0-5)

### Citations

**File:** contracts/controller/src/lib.rs (L167-179)
```rust
    /// Flash-loans `amount` of `asset` to a deployed Wasm `receiver`, invoking
    /// its callback with `data`. The pool recovers principal plus fee before return.
    /// Permissionless; requires caller authorization.
    #[when_not_paused]
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

**File:** contracts/pool/src/ops/flash.rs (L140-167)
```rust
fn invoke_receiver(
    env: &Env,
    cache: &Cache,
    receiver: &Address,
    initiator: Address,
    amount: i128,
    fee: i128,
    pool: &Address,
    data: Bytes,
) {
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
}

/// Pulls principal + fee via `transfer_from` after verifying allowance.
fn collect_repayment(
    env: &Env,
```
