I found a directly analogous authorization gap in the `check_actor_permissions` function that governs which actions require the caller to be the account owner.

### Title
Missing actor-permission check on `TransferToGasKey` allows anyone to fund/consume a victim's gas key allowance without authorization - (File: `runtime/runtime/src/actions.rs`)

### Summary
Just as `CredibleAccountModule::validateSessionKeyParams()` was left `public` and mutated `TokenData` state for an arbitrary victim account, nearcore's `check_actor_permissions` function explicitly whitelists `Action::TransferToGasKey` (alongside `CreateAccount`, `FunctionCall`, `Transfer`) as an action that does **not** require `actor_id == account_id` [1](#0-0) . This means any predecessor (any account, or any contract acting as predecessor via a cross-contract call) can trigger a `TransferToGasKey` action against an arbitrary receiver account's gas key, unlike `AddKey`/`DeleteKey`/`Stake`/`DeleteAccount`, which strictly enforce `actor_id == account_id`.

### Finding Description
`action_transfer_to_gas_key` mutates the gas key's prepaid balance for the given `(account_id, public_key)` pair [2](#0-1) . The dispatch table in `check_actor_permissions` only enforces `actor_id == account_id` for `AddKey`, `DeleteKey`, `Stake`, and `DeleteAccount` [3](#0-2) , but `Action::TransferToGasKey` is bundled with `CreateAccount`/`FunctionCall`/`Transfer` in the no-check branch [4](#0-3) . This mirrors the Solidity bug class exactly: a state-mutating function that is supposed to be gated to a privileged caller (in Solidity, "only via `validateUserOp`"; in nearcore, "only the owning account should mutate its own access key") is instead reachable by any unprivileged predecessor, because the authorization check is missing from the allow-list.

Note: unlike `TransferToGasKey`, funds moving *out* of a gas key (`WithdrawFromGasKey`) credit the account's own `amount`, so it is not directly a theft vector on its own; the primary impact here is that anyone can force deposits into (and thus interact with) a victim's gas key `(account_id, public_key)`, unauthorized griefing/state-mutation on an account the caller does not own. Given the limited scope of source material retrieved, I was not able to fully verify whether `TransferToGasKey`'s inclusion in the exempted branch is intentional (e.g., is TransferToGasKey deliberately meant to permit third-party top-ups, similar to `Transfer`, since it just adds balance and cannot be used to steal funds) versus an oversight equivalent to the Solidity report. This ambiguity matters because, unlike the Solidity bug (which enabled outright fund/token theft via unauthorized claim), `TransferToGasKey` only *adds* balance to the target — it does not let an attacker withdraw or consume the victim's existing balance. That functional difference significantly weakens the "concrete token inflation or theft, unauthorized state or balance change" bar required for a valid finding here.

### Impact Explanation
If unintentional, this would allow any account to insert deposits into an arbitrary account's gas key without consent, which is an unauthorized state mutation, but it does not by itself let anyone drain, claim, or lock funds belonging to the victim (the deposited funds remain credited to the victim's own gas key). This differs materially from the Solidity C-05 report, where the public function allowed an attacker to consume/lock a victim's tokens and prevent them from being unlocked (a direct griefing/DoS + fund-lock condition). I could not find a comparable irreversible-lock/consumption effect from an unauthorized `TransferToGasKey` call in the retrieved code.

### Likelihood Explanation
Reachable trivially from any submitted transaction with a `TransferToGasKey` action targeting an arbitrary `receiver_id`, since no signature/actor check gates it beyond the general receipt validity rules.

### Recommendation
Confirm the intended semantics of `TransferToGasKey`. If it is meant to be restricted to the key/account owner (matching `AddKey`), add it to the `actor_id == account_id` branch in `check_actor_permissions` (`runtime/runtime/src/actions.rs`). If third-party top-ups are an intended feature (analogous to plain `Transfer`), then this is not a vulnerability and should be excluded.

### Proof of Concept
Not constructed — I was unable to fully confirm exploitability/impact severity (whether unauthorized `TransferToGasKey` produces any state change beyond a benign balance top-up) using the available indexed code alone. A background Devin session with full repository and test-execution access would be needed to write and run a reproduction transaction and confirm whether this exempted action is an intentional design choice or an authorization-check omission with real security impact.

### Citations

**File:** runtime/runtime/src/actions.rs (L760-776)
```rust
        }
        Action::DeleteAccount(_) => {
            if actor_id != account_id {
                return Err(ActionErrorKind::ActorNoPermission {
                    account_id: account_id.clone(),
                    actor_id: actor_id.clone(),
                }
                .into());
            }
            let account = account.as_ref().unwrap();
            if !account.locked().is_zero() {
                return Err(ActionErrorKind::DeleteAccountStaking {
                    account_id: account_id.clone(),
                }
                .into());
            }
        }
```

**File:** runtime/runtime/src/actions.rs (L777-783)
```rust
        Action::CreateAccount(_)
        | Action::FunctionCall(_)
        | Action::Transfer(_)
        | Action::TransferToGasKey(_) => (),
        Action::Delegate(_) | Action::DelegateV2(_) => (),
        Action::DeterministicStateInit(_) => (),
    };
```

**File:** protocol-model/spec/accounts-keys.md (L48-48)
```markdown
Gas-key balance is moved through dedicated actions (never via AddKey): `action_transfer_to_gas_key` (`:257`) `checked_add`s a deposit to `GasKeyInfo.balance`; `action_withdraw_from_gas_key` (`:290`) subtracts from the gas-key balance (erroring `InsufficientGasKeyBalance` on underflow, `:316`) and credits the account `amount` (`:333`). Both error `GasKeyDoesNotExist` if the key is absent or not a gas key (`:264`,`:271` / `:298`,`:305`).
```
