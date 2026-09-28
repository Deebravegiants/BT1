### Title
User-controlled token addresses and amounts injected into controller invoker auth in `migrate_from_blend` — arbitrary `transfer(controller → blend_pool)` authorization ([File: contracts/controller/src/external/blend.rs])

### Summary
The Blend migration path builds `InvokerContractAuthEntry` trees granting `token.transfer(controller → blend_pool, max)` for every `(debt_asset, max)` pair the caller supplies in `debt_caps`, and uses a caller-supplied `blend_pool` as the payee — the same bug class as CVE-2026-73073: an attacker-controlled value is spliced, unvalidated, into a command executed under the contract's own authority.

### Finding Description
`authorize_repay_pulls` iterates the caller-provided `debt_caps: Vec<(Address, i128)>` and, for each pair, authorizes on behalf of the controller a `transfer` from `env.current_contract_address()` to the caller-provided `blend_pool` address:

- `contract: debt_asset` — taken directly from the caller's argument, with no check that it is a listed hub/spoke asset or a real Blend debt token.
- `to: blend_pool` — the caller-supplied pool address, not a stored/allowlisted contract.
- `amount: max` — the caller-supplied cap, unbounded by any actual debt.
- `sub_invocations: Vec::new` — a leaf entry, so the authorized transfer needs nothing further. [1](#0-0) 

Soroban invoker-contract auth satisfies the `from.require_auth()` inside `token.transfer` whenever that transfer is invoked as a sub-invocation of the controller's next outbound call. Because `blend_pool` is attacker-controlled, the controller's next call is into the attacker's own contract, which simply invokes `token.transfer(controller, attacker_pool, max)` on the named asset — the injected auth entry makes it succeed. The single unprivileged path is `controller.migrate_from_blend(blend_pool=<attacker contract>, debt_caps=[(victim_token, i128::MAX)], …)`.

The same anti-pattern in the intended integration is documented as safe only when the auth is created "against an address your contract stored, never one the caller passes" (`skills/xoxno-lending-contracts/SKILL.md` contract-caller rule 7) — `authorize_repay_pulls` violates exactly this rule for both the token address and the recipient.

### Impact Explanation
Any token balance held by the controller address at the moment `migrate_from_blend` executes — accumulated transfer-measurement leftovers, excess-payment refund dust, rounding residue, or unclaimed amounts (`multiply` initial payments are routed `caller → controller`, per `skills/xoxno-lending-contracts/composing.md` and `contracts/controller/src/strategies/swap.rs`) — can be pulled to an attacker contract for every token address the attacker lists in `debt_caps`, up to the supplied `max`. This is theft of funds and theft of unclaimed yield held at the controller, reachable by a single unprivileged address with no prerequisite position.

### Likelihood Explanation
The entrypoint is permissionless (`migrate_from_blend` is on the in-scope unprivileged list), the `debt_caps` and `blend_pool` arguments are caller data, and the attacker's contract is invoked as the very next sub-call, which is precisely what invoker auth requires. The only mitigating factor is that profit is bounded by the controller's live token balances; if the controller holds no idle balance of the named token, the transfer simply moves zero/mints nothing — but it costs the attacker nothing to attempt across many tokens in one `debt_caps` vector. Caveat: I could not fully verify whether `migrate_from_blend` additionally validates `blend_pool`/`debt_asset` elsewhere in its flow (e.g., against stored Blend deployment addresses or listed spoke assets); if it does, the issue collapses.

### Recommendation
Do not build auth entries from caller-supplied identifiers. Pin `blend_pool` to a configured/allowlisted Blend pool (or derive it per `debt_asset` from stored config), validate every `debt_asset` in `debt_caps` against the set of tokens the Blend pool can actually pull (queried from the real Blend pool, not from args), and cap each `max` at the debt amount reported by Blend. Analogous to the Vim fix (escaping the interpolated value), the auth context must be constructed entirely from trusted state.

### Proof of Concept
```rust
// Attacker contract standing in for `blend_pool`
#[contractimpl]
impl FakeBlend {
    // whatever entrypoint migrate_from_blend calls on blend_pool
    pub fn repay(env: Env, asset: Address, amount: i128) {
        let controller = /* invoker */;
        // Inside this sub-invocation the controller's pre-authorized
        // transfer(controller -> self, max) satisfies `controller` auth.
        token::Client::new(&env, &asset).transfer(&controller, &env.current_contract_address(), &amount);
    }
}

// Caller side:
// controller.migrate_from_blend(
//     caller, account_id,
//     blend_pool = fake_blend_addr,                // attacker contract
//     debt_caps  = vec![(usdc, i128::MAX), (xlm, i128::MAX), ...],
//     ...
// );
// -> each listed token's controller balance is pulled to fake_blend_addr.
```
Root cause is `authorize_repay_pulls` at `contracts/controller/src/external/blend.rs:103-119` constructing `SubContractInvocation` auth trees directly from `debt_caps`/`blend_pool` arguments.

### Citations

**File:** contracts/controller/src/external/blend.rs (L103-119)
```rust
fn authorize_repay_pulls(env: &Env, blend_pool: &Address, debt_caps: &Vec<(Address, i128)>) {
    if debt_caps.is_empty() {
        return;
    }
    let controller = env.current_contract_address();
    let mut entries: Vec<InvokerContractAuthEntry> = Vec::new(env);
    for (debt_asset, max) in debt_caps.iter() {
        entries.push_back(InvokerContractAuthEntry::Contract(SubContractInvocation {
            context: ContractContext {
                contract: debt_asset,
                fn_name: symbol_short!("transfer"),
                args: (controller.clone(), blend_pool.clone(), max).into_val(env),
            },
            sub_invocations: Vec::new(env),
        }));
    }
    env.authorize_as_current_contract(entries);
```
