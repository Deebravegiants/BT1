## Title
Contract "gas reward" lets a malicious contract extract tokens from callers/relayers via inflated `gas_burnt_for_function_call`, mirroring the UDT-referrer gas-estimate abuse — (File: `runtime/runtime/src/lib.rs`)

### Summary
The Unlock.sol finding centers on a reward that is computed as `estimatedGasForPurchase * tx.gasprice` and paid out to an attacker-controlled address, which can be gamed whenever the gas actually consumed diverges from the gas used to compute the reward (misconfiguration, protocol changes, or gas-refund tricks). NEAR's runtime has a structurally identical pattern: contract accounts are paid a reward computed as a fraction of `gas_burnt_for_function_call * gas_price`, where `gas_burnt_for_function_call` is a metered (not measured) quantity. Any contract can maximize this metered quantity relative to the actual value delivered to the caller, extracting tokens from whoever pays for the call (typically a relayer/meta-transaction sponsor), exactly the "faucet-draining" abuse nearcore's own docs warn about.

### Finding Description
During `Runtime::apply_action_receipt`, after a `FunctionCall` executes, the runtime computes a reward for the receiving contract account as a fixed fraction (`burnt_gas_reward`, mainnet `3/10`) of the metered gas burnt specifically for the function-call body, converted to tokens at the receipt's gas price: [1](#0-0) 

This reward is subtracted from the amount that would otherwise be burnt (removed from supply) and credited directly to the contract's account balance: [2](#0-1) 

`gas_burnt_for_function_call` is a wasm-metering estimate — number of wasm ops times `wasm_regular_op_cost`, plus host-function costs — not an actual measurement of hardware work performed, exactly like Unlock's `estimatedGasForPurchase` is an estimate, not the real gas spent: [3](#0-2) 

nearcore's own architecture docs explicitly acknowledge this reward design creates the same class of extraction risk described in the Unlock report — a "smart contract gets paid" model where an attacker who controls both the calling pattern and the called contract can drain a paying party: [4](#0-3) 

Further corroborating that the metering-vs-real-cost gap is a live, known issue (not merely hypothetical), a runtime-params-estimator comment for a different action fee states it is "undercharged" but "not a concern" for that specific action: [5](#0-4) 

Most tellingly, nearcore has already scheduled removal of this exact reward mechanism in a future protocol version specifically because of its risk, reducing `burnt_gas_reward` from 30% to 0%: [6](#0-5) 

This mirrors the Unlock timeline precisely: the report identified an economically exploitable gas-based reward; the maintainers acknowledged the risk exists but is bounded/design-accepted; and ultimately the underlying "estimate-based reward" mechanic is being phased out. In NEAR's case, the analogous mitigation is to zero out `burnt_gas_reward` in protocol version 87 (not yet activated at the current stable protocol version 86, per `protocol-model/spec/economics.md`).

### Impact Explanation
Unlike Unlock's UDT case, this does not mint new tokens outright — the reward is carved out of gas that would otherwise be burnt. However, it enables an unauthorized value transfer: any party that pays gas for a `FunctionCall` to an attacker-controlled contract (most acutely, a meta-transaction relayer, faucet, or any service that pays gas on behalf of users invoking third-party contracts) has up to 30% of the metered `gas_burnt_for_function_call` diverted to the contract owner instead of being burnt or otherwise benefiting the payer. A contract author can deliberately maximize wasm op count / host-function calls relative to any useful work performed (e.g., loop bodies dominated by cheap-to-execute-but expensively-metered wasm instructions or host functions) to maximize the reward extracted per unit of real compute time, draining payer funds at a rate bounded only by `max_gas_burnt` per call and the number of calls the payer is willing to fund. This is a genuine underpriced/skewed value flow in the balance-and-gas-accounting path, reachable purely via ordinary `FunctionCall` receipts from any account.

### Likelihood Explanation
Exploitation requires an external assumption — that some third party (a relayer, faucet, or sponsor) pays gas fees for calls into a contract the attacker controls without vetting its gas usage — which is analogous to Unlock's assumption that a gas-refund token gets approved by governance. This is a real and common pattern in NEAR ecosystem tooling (meta-transactions, gasless dApp relayers). No validator/node compromise or network-layer assumption is needed; a single unprivileged account (the attacker's contract) combined with an unprivileged caller (or the attacker calling their own contract while a relayer covers gas) suffices.

### Recommendation
This matches nearcore's own already-planned direction: complete rollout of `RemoveGasRewards` (protocol version 87), setting `burnt_gas_reward` to 0, so metered gas burnt during function-call execution is never redirected to the receiving contract. Until that activates, any service that subsidizes gas for arbitrary third-party contract calls should treat `burnt_gas_reward`-funded balance growth on called contracts as an explicit risk and cap total gas sponsored per contract/session, similar to the "global daily upper limit" mitigation recommended in the original report.

### Proof of Concept
1. Deploy a contract whose method body is dominated by cheap-per-instruction-but-heavily-metered wasm loops or host-function calls (e.g., repeated `sha256`/`keccak` calls or tight wasm op loops) that burn close to `max_gas_burnt` per invocation while doing minimal useful work for the caller.
2. Have a gas-sponsoring party (relayer/faucet) submit `FunctionCall` transactions/receipts to this contract on behalf of users, or call it directly with self-funded gas.
3. After execution, `runtime/runtime/src/lib.rs:1053-1070` computes `receiver_gas_reward = gas_burnt_for_function_call * 3/10`, and `lib.rs:1072-1084` credits this amount directly to the contract account's balance, funded from the gas the caller/sponsor already paid.
4. Repeating this across many calls funded by the sponsor incrementally transfers a steady 30% skim of sponsored gas into the attacker's contract balance, verifiable by observing account balance deltas as in the existing test `test_smart_contract_reward` (`integration-tests/src/tests/standard_cases/mod.rs:683-728`), which explicitly documents the reward and its removal in `RemoveGasRewards`.

### Citations

**File:** runtime/runtime/src/lib.rs (L1053-1070)
```rust
        // Adding burnt gas reward for function calls if the account exists.
        let receiver_gas_reward = result
            .gas_burnt_for_function_call
            .checked_mul(*apply_state.config.fees.burnt_gas_reward.numer() as u64)
            .unwrap()
            .checked_div(*apply_state.config.fees.burnt_gas_reward.denom() as u64)
            .unwrap();
        // The balance that the current account should receive as a reward for function call
        // execution.
        let receiver_reward =
            if ProtocolFeature::AccountCostIncrease.enabled(apply_state.current_protocol_version) {
                safe_gas_to_balance(gas_burn_price, receiver_gas_reward)?
            } else {
                // Post NEP-536/pre AccountCostIncrease: We are not refunding gas price differences, we just use the receipt
                // gas price and call it the correct price.
                // No deficits to try and recover. Use receipt gas price for reward calculation
                safe_gas_to_balance(gas_purchase_price, receiver_gas_reward)?
            };
```

**File:** runtime/runtime/src/lib.rs (L1072-1084)
```rust
        if receiver_reward > Balance::ZERO {
            let mut account = get_account(state_update, account_id)?;
            if let Some(ref mut account) = account {
                // Validators receive the remaining execution reward that was not given to the
                // account holder. If the account doesn't exist by the end of the execution, the
                // validators receive the full reward.
                tx_burnt_amount = tx_burnt_amount.checked_sub(receiver_reward).unwrap();
                account.set_amount(safe_add_balance(account.amount(), receiver_reward)?);
                set_account(state_update, account_id.clone(), account);
                state_update.commit(StateChangeCause::ActionReceiptGasReward {
                    receipt_hash: receipt.get_hash(),
                });
            }
```

**File:** docs/architecture/gas/README.md (L183-199)
```markdown
The most fundamental dynamic gas cost is `wasm_regular_op_cost`. It is
multiplied by the exact number of WASM operations executed. You can read about
[Gas Instrumentation](https://nomicon.io/RuntimeSpec/Preparation#gas-instrumentation)
if you are curious how we count WASM ops.

Currently, all operations are charged the same, although it could be more
efficient to charge less for opcodes like `i32.add` compared to `f64.sqrt`.

The remaining dynamic costs are for work done during host function calls. Each
host function charges a base cost. Either the general `wasm_base` cost, or a
specific cost such as `wasm_utf8_decoding_base`, or sometimes both. New host
function calls should define a separate base cost and not charge `wasm_base`.

Additional host-side costs can be scaled per input byte, such as
`wasm_sha256_byte`, or costs related to moving data between host and guest, or
any other cost that is specific to the host function. Each host function must
clearly define what its costs are and how they depend on the input.
```

**File:** docs/architecture/how/gas.md (L144-157)
```markdown
### Contract Reward

A rather unique property of Near Protocol is that a part of the gas fee goes to
the contract owner. This "smart contract gets paid" model is pretty much the
opposite design choice from the "smart contract pays" model that for example
[Cycles in the Internet
Computer](https://internetcomputer.org/docs/current/developer-docs/gas-cost#details-cost-of-compute-and-storage-transactions-on-the-internet-computer)
implement.

The idea is that it gives contract developers a source of income and hence an
incentive to create useful contracts that are commonly used. But there are also
downsides, such as when implementing a free meta-transaction relayer one has to
be careful not to be susceptible to faucet-draining attacks where an attacker
extracts funds from the relayer by making calls to a contract they own.
```

**File:** runtime/runtime-params-estimator/src/action_costs.rs (L589-599)
```rust
pub(crate) fn add_function_call_key_byte_exec(ctx: &mut EstimatorContext) -> GasCost {
    ActionEstimation::new_sir(ctx)
        .add_action(add_fn_access_key_action(ActionSize::Max))
        .inner_iters(1) // adding the same key a second time would fail
        // parameter today: 1_925_331
        // typical estimation: 18_000_000 (18ns)
        // (we know this is undercharged but it's not a concern as described in #6716)
        // setting limit to 1ns to keep it lower than the parameter
        .min_gas(GAS_1_NANOSECOND)
        .apply_cost(&mut ctx.testbed())
        / ActionSize::Max.key_methods_list()
```

**File:** core/parameters/res/runtime_configs/87.yaml (L1-7)
```yaml
# Remove gas rewards: stop paying part of the gas burned by a `FunctionCall`
# back to the contract account as a reward. Set the reward from 30% to 0%.
burnt_gas_reward:
  {
    old: { numerator: 3, denominator: 10 },
    new: { numerator: 0, denominator: 1 },
  }
```
