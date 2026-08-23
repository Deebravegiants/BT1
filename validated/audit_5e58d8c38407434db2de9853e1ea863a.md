### Title
Wallet-contract relayer can double-claim the "fee" reward by paying it out unconditionally and then refunding the full original deposit on transaction failure - (File: `runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs`)

### Summary
`near-wallet-contract`'s `inner_rlp_execute` pays a relayer `fee` to the `predecessor_account_id` unconditionally, before the underlying emulated Ethereum action (base-token transfer or ERC-20 transfer) has actually executed. If that underlying action later fails, `rlp_execute_callback` refunds the *entire* original `attached_deposit` (tracked as `CallerDeposit`) back to the same predecessor, without subtracting the `fee` that was already paid out. This is structurally the same bug class as the PixelSwap report: a message/callback that credits a counterparty as if nothing had been spent, while in fact part of the funds were already unconditionally disbursed, letting the counterparty collect more than they put in.

### Finding Description
`inner_rlp_execute` records the caller's whole payable deposit as a `CallerDeposit` for later refund purposes: [1](#0-0) 

Before the actual action promise is built, if the parsed transaction is an `EOABaseTokenTransfer` or `ERC20Transfer` with a non-zero `fee`, the contract immediately (unconditionally, independent of whether the transfer itself will succeed) creates a transfer promise paying `fee` to the predecessor: [2](#0-1) 

The value that gets refunded to the same predecessor when the *underlying* action later fails is the full `yocto_near` (the whole original attached deposit) stored in `CallerDeposit`, with no accounting for the `fee` that was already paid out at the top of the call: [3](#0-2) 

`CallerDeposit` itself is constructed straight from `context.attached_deposit`, i.e. the whole deposit physically attached to the `rlp_execute` call, with no reduction for the fee that is going to be carved out of it: [4](#0-3) 

The net effect: the wallet contract sends `fee` to the relayer up front from its own balance (funded by the deposit that was just attached), and then — if the relayer arranges for the "real" action to fail — refunds the *entire* original deposit (which conceptually already included the fee's worth of value) back to that same relayer. This is analogous to the PixelSwap `unspent_order_inputs` bug: a failure-handling code path assumes tokens were "not spent" and credits them back in full, while in fact the settlement (here, `fee`) had already been spent/paid unconditionally, letting the actor recoup more value than they actually contributed.

### Impact Explanation
A malicious or self-serving relayer (an unprivileged account, since anyone can call `rlp_execute` and act as `predecessor_account_id`) can pick a transaction that:
1. Specifies a non-zero `fee` for an `EOABaseTokenTransfer`/`ERC20Transfer`.
2. Is crafted so that the *underlying* promise (the emulated transfer itself) will fail — e.g., targeting an account/token that will reject the call, exhausting gas on that step, or other failure conditions reachable through the eth-emulation path.

In that scenario the relayer receives the `fee` immediately (step at lines 367-385) and then additionally receives a full refund of the original attached deposit through `rlp_execute_callback`'s `Failed` branch, because the refund does not net out the `fee` already sent. This drains value from the eth-implicit wallet account's own balance (or from whatever surplus the deposit represented beyond the actual required action value) with each such crafted transaction, i.e., unauthorized balance loss for the wallet-contract account and unearned/inflated compensation for the relayer.

### Likelihood Explanation
This requires no privileged role — `rlp_execute` is a public, payable entry point intended to be called by arbitrary relayers on behalf of eth-implicit accounts, and the attacker only needs to control the `predecessor_account_id` (i.e., be the one submitting/relaying the transaction) and be able to shape the emulated transaction so the underlying action fails while `fee` is non-zero. The fee-payout and failure-refund code paths are both reachable through ordinary transaction submission with no special account permissions.

### Recommendation
- Short term: subtract the already-paid `fee` from the amount tracked/refunded in `CallerDeposit` before creating the fee-transfer promise, or defer paying the `fee` until the underlying action's success is confirmed (e.g., pay it from within the success branch of `rlp_execute_callback` instead of unconditionally at the top of `inner_rlp_execute`).
- Long term: document/test the full success and failure flows of the fee-and-refund mechanism (similar to the recommendation in the source report), specifically covering the interaction between `fee` payout, `CallerDeposit` tracking, and the `Failed` branch of `rlp_execute_callback`, to ensure the sum of "fee paid" + "deposit refunded" never exceeds the originally attached deposit.

### Proof of Concept
Conceptual sequence based on the code paths cited above (exact wasm-level PoC was not runnable in this analysis, but the logical flow is fully supported by the cited code):
1. Attacker acts as the relayer/`predecessor_account_id` and calls `rlp_execute` on a target wallet contract, attaching a deposit `D` and submitting an RLP-encoded `ERC20Transfer` (or `EOABaseTokenTransfer`) transaction with a non-zero `fee = F` (`F < D`).
2. `inner_rlp_execute` immediately queues a transfer of `F` to the attacker (lines 367-385), funded from the wallet contract's balance.
3. `CallerDeposit { account_id: attacker, yocto_near: D }` is carried through to `rlp_execute_callback` (lines 340-345).
4. The attacker crafts the transaction so the actual emulated transfer/cross-contract call fails (e.g., invalid/non-existent target token or account, or a call guaranteed to hit `PromiseResult::Failed`).
5. `rlp_execute_callback`'s `Failed` branch refunds the full `D` back to the attacker (lines 296-312).
6. Net attacker gain: `F` (unjustified), extracted from the wallet contract's own balance across one call; repeatable to drain the account.

### Citations

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L296-312)
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

                ExecuteResponse {
                    success: false,
                    success_value: None,
                    error: Some("Failed Near promise".into()),
                }
            }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L340-345)
```rust
    let context = ExecutionContext::new(
        current_account_id.clone(),
        predecessor_account_id,
        env::attached_deposit(),
    )?;
    let caller_deposit = CallerDeposit::new(&context);
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L367-385)
```rust
            // If the action is an emulated base token or ERC-20 transfer with a non-zero fee then
            // create a promise to send the refund to the relayer. This allows any relayer
            // to safely serve base token transfers from any wallet without additional
            // on-boarding because the relayer will receive some compensation for sending
            // the transaction. Users should always verify the fee before signing a base token
            // transfer. Relayers should also verify the fee before sending to make sure the
            // user's signed transaction will refund enough to cover the relayer's gas costs.
            if let TransactionKind::EthEmulation(EthEmulationKind::EOABaseTokenTransfer {
                fee,
                ..
            })
            | TransactionKind::EthEmulation(EthEmulationKind::ERC20Transfer { fee, .. }) =
                &transaction_kind
            {
                if !fee.is_zero() && context.predecessor_account_id != context.current_account_id {
                    let refund_promise = env::promise_batch_create(&context.predecessor_account_id);
                    env::promise_batch_action_transfer(refund_promise, *fee);
                }
            }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/types.rs (L172-191)
```rust
/// A data type to keep track of the deposit given by an external caller.
/// This allows us to refund the caller's deposit if the cross-contract call fails.
#[derive(Debug, PartialEq, Eq, Clone, serde::Serialize, serde::Deserialize)]
pub struct CallerDeposit {
    pub account_id: AccountId,
    pub yocto_near: NonZeroU128,
}

impl CallerDeposit {
    pub fn new(context: &ExecutionContext) -> Option<Self> {
        // Only track for external (non-self) callers
        if context.current_account_id == context.predecessor_account_id {
            return None;
        }

        NonZeroU128::new(context.attached_deposit.as_yoctonear()).map(|yocto_near| Self {
            account_id: context.predecessor_account_id.clone(),
            yocto_near,
        })
    }
```
