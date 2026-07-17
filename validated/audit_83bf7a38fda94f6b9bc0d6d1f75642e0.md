### Title
`rlp_execute` is `#[payable]` but silently absorbs attached NEAR on early-return failure paths — (`File: runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs`)

### Summary

The `rlp_execute` entry point of the NEAR Wallet Contract (deployed for every ETH-implicit account) is marked `#[payable]`, meaning any caller can attach NEAR tokens to the call. However, two distinct early-return code paths return `PromiseOrValue::Value(...)` (a successful, non-panicking return) without refunding the attached deposit. In NEAR Protocol, a deposit is only automatically refunded when a function call **panics**; a successful return keeps the deposit in the contract. The absorbed NEAR is then part of the wallet contract's balance and can be drained by the wallet owner via a subsequent valid Transfer action.

### Finding Description

`rlp_execute` is declared `#[payable]` at line 88: [1](#0-0) 

Two code paths return a successful `PromiseOrValue::Value(...)` without issuing any refund:

**Path 1 — in-flight transaction guard** (lines 97–105): If `has_in_flight_tx` is `true`, the function returns immediately with a value response. Any attached deposit is silently absorbed. [2](#0-1) 

**Path 2 — non-relayer errors from `inner_rlp_execute`** (line 126): User errors (`EvmDeployDisallowed`, `ExcessYoctoNear`, `ValueTooLarge`, `UnsupportedAction(AddFullAccessKey)`) and account-ID errors (`AccountIdTooShort`, `Missing0xPrefix`, `InvalidHex`) all propagate to this arm and return a value response, again absorbing the deposit. [3](#0-2) 

The `CallerDeposit` refund mechanism (tracked in `inner_rlp_execute` and executed in `rlp_execute_callback`) only fires when a cross-contract promise is actually created and later fails. It is never reached in either of the two paths above. [4](#0-3) [5](#0-4) 

### Impact Explanation

The absorbed NEAR becomes part of the wallet contract's account balance. The wallet owner (holder of the ETH private key) can immediately drain it by submitting a valid signed Ethereum Transfer transaction through `rlp_execute`, directing the wallet's full balance to any account they control. The corrupted protocol value is the **NEAR balance** of the ETH-implicit account: it is inflated by the victim's deposit and then transferred out by the wallet owner, resulting in a direct, irreversible loss of funds for the caller.

### Likelihood Explanation

Likelihood is low-to-medium. External callers (e.g., relayers or dApp frontends) may attach NEAR to `rlp_execute` intending it to fund the cross-contract action, not realising the call will fail (wrong nonce, wrong chain ID, unsupported action type, or a concurrent in-flight transaction). The wallet contract is deployed for every ETH-implicit account on NEAR mainnet, so the attack surface is broad. No special privileges are required: any unprivileged account can call `rlp_execute` with an attached deposit.

### Recommendation

Remove `#[payable]` from `rlp_execute` and instead require callers to attach the deposit to the inner action via the Ethereum transaction's `value` field and the `yocto_near` action parameter, which are already the intended mechanisms. If `#[payable]` must be retained for relayer-refund use cases, add an explicit refund of `env::attached_deposit()` to `predecessor_account_id()` in every early-return path that does not create a promise.

### Proof of Concept

1. Wallet owner's ETH-implicit account `0xABCD…` has `has_in_flight_tx = false`.
2. Wallet owner initiates a valid transaction, setting `has_in_flight_tx = true`.
3. Victim calls `rlp_execute` on `0xABCD…` with `attached_deposit = 10 NEAR` while `has_in_flight_tx == true`. The call returns `PromiseOrValue::Value(ExecuteResponse { success: false, … })` — a successful NEAR transaction — and the 10 NEAR is credited to `0xABCD…`'s balance.
4. After the in-flight transaction resolves (`has_in_flight_tx` resets to `false`), the wallet owner submits a signed Ethereum Transfer transaction for `10 NEAR` to their own account. `rlp_execute` succeeds and the 10 NEAR is transferred out.

The same scenario applies when the victim's call fails due to a user error (e.g., `tx.to == None` → `EvmDeployDisallowed`, or an unsupported `AddFullAccessKey` action), which also hits the `Err(e) => PromiseOrValue::Value(e.into())` path at line 126. [6](#0-5)

### Citations

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L88-93)
```rust
    #[payable]
    pub fn rlp_execute(
        &mut self,
        target: AccountId,
        tx_bytes_b64: String,
    ) -> PromiseOrValue<ExecuteResponse> {
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L97-105)
```rust
        if self.has_in_flight_tx {
            return PromiseOrValue::Value(ExecuteResponse {
                success: false,
                success_value: None,
                error: Some(
                    "Error: transaction already in progress, please try again later.".into(),
                ),
            });
        }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L116-127)
```rust
        match result {
            Ok(promise) => {
                self.has_in_flight_tx = true;
                PromiseOrValue::Promise(promise)
            }
            Err(Error::Relayer(_)) if env::signer_account_id() == current_account_id => {
                let promise = create_ban_relayer_promise(current_account_id);
                self.has_in_flight_tx = true;
                PromiseOrValue::Promise(promise)
            }
            Err(e) => PromiseOrValue::Value(e.into()),
        }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L296-305)
```rust
        match env::promise_result(0) {
            PromiseResult::Failed => {
                // The cross-contract call failed, refund the caller if needed
                if let Some(CallerDeposit { account_id, yocto_near }) = caller_deposit {
                    let refund_promise = env::promise_batch_create(&account_id);
                    env::promise_batch_action_transfer(
                        refund_promise,
                        NearToken::from_yoctonear(yocto_near.into()),
                    );
                }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L330-345)
```rust
fn inner_rlp_execute(
    current_account_id: AccountId,
    predecessor_account_id: AccountId,
    target: AccountId,
    tx_bytes_b64: String,
    nonce: &mut u64,
) -> Result<Promise, Error> {
    if *nonce == u64::MAX {
        return Err(Error::AccountNonceExhausted);
    }
    let context = ExecutionContext::new(
        current_account_id.clone(),
        predecessor_account_id,
        env::attached_deposit(),
    )?;
    let caller_deposit = CallerDeposit::new(&context);
```
