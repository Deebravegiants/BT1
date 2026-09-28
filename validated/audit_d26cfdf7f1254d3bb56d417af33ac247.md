### Title
Caller-supplied `receiver` contract is invoked beneath the caller's `require_auth` tree, letting a malicious callback transfer arbitrary tokens out of the initiator's wallet - ([File: contracts/controller/src/strategies/flash_position.rs](contracts/controller/src/strategies/flash_position.rs))

### Summary
`flash_position` lets any caller name an arbitrary contract as `receiver`. The controller then invokes `execute_flash_position` on that address inside the same transaction that carries `caller.require_auth()` (`require_authorized_caller`). In Soroban, an invocation made by that third-party contract — e.g. `token.transfer(caller, attacker, balance)` — is recorded by the transaction simulator as a child of the caller's authorization entry. If the user signs the simulated tree (which clients produce automatically), the malicious receiver can drain any token in the caller's wallet. This is the Soroban analog of interpolating an unvalidated, attacker-controlled value (`GIT_DIR`) into a privileged execution context: user input is placed unquoted/unvalidated onto the call stack under the user's authority.

### Finding Description
- `process_flash_position` authenticates only the caller via `require_authorized_caller(env, caller)` at line 45, then accepts `receiver: &Address` straight from user arguments (lines 31, 47-57).
- The only validation is `require_wasm_receiver` and exclusion of the controller and pool addresses (lines 69-84). Any other deployed contract — including an attacker-deployed one — is accepted.
- `invoke_receiver` performs `env.invoke_contract(receiver, "execute_flash_position", ...)` at lines 308-322, putting arbitrary third-party code on the call stack *below the caller's authorization entry*.
- The flash guard (`storage::with_flash_guard`, line 121) blocks reentry into controller monetary functions, but does not restrict what the receiver contract itself does — including calling `token.transfer(caller, attacker, x)` on any token the caller holds.
- The companion test `tests/test-harness/tests/strategy/rogue_hop_pool_transfer_joins_caller_auth_tree.rs` proves the mechanism end-to-end for the router path: a rogue contract invoked under the caller's auth entry gets its `transfer(victim, attacker, WALLET_BALANCE)` recorded as a child of the caller's entry in simulation (lines 194-227) and executes when the signed tree includes it (lines 258-268). The identical mechanism applies here because `flash_position`'s receiver is reached beneath the caller's `require_auth` in exactly the same way.

### Impact Explanation
Theft of user funds. A crafted `flash_position` request (delivered via a malicious frontend, quote, or phishing payload) names an attacker-controlled `receiver`. During `simulateTransaction`, the receiver's `token.transfer(victim, attacker, victim_balance)` is appended as a sub-invocation under the victim's `flash_position` auth entry. A victim who signs the produced tree authorizes that transfer, and the attacker receives tokens the protocol never listed or touched — the victim's entire wallet balance of an arbitrary token, as demonstrated by `WALLET_BALANCE` being fully drained in the test (lines 224-225, 267-268).

### Likelihood Explanation
Reachable by a single unprivileged address through `flash_position(caller, account_id, spoke_id, mode, debt, amount, receiver, data, collaterals, refund_assets)` — `receiver` is a free `Address` argument with no allowlist. Exploitation requires the victim to sign an authorization tree containing the extra child entry; standard wallets/clients sign whatever `simulateTransaction` returns, and the in-repo test confirms recording mode silently attaches the rogue transfer. The attack does not require defeating any economic check, since no controller/pool funds move to the attacker — the loss lands on the caller's wallet, so `strategy_finalize`, health-factor gates, and `require_flash_position_still_open` all still pass (the victim's account stays solvent; the stolen funds were never part of the position).

### Recommendation
Treat external code invoked beneath user auth the way shell metacharacters are treated in the original report — quote/constrain it:
- Restrict `receiver` to a governance- or hub-allowlisted set of flash-receiver contracts, or require that `receiver` be a protocol-known adapter, rather than an arbitrary address.
- Alternatively, document and enforce at the client/SDK boundary that the signed auth tree for `flash_position` must contain no child invocations other than the expected ones (an honest flow produces none under the caller's entry), mirroring the guidance already given for router swaps in `docs/explanation/threat-model.md`.
- Emit the receiver address in the event (already done via `FlashPositionEvent.receiver`) so monitoring can flag unlisted receivers.

### Proof of Concept
1. Attacker deploys `RogueReceiver` — a contract whose `execute_flash_position(env, initiator, account_id, asset, amount, fee, amount_received, controller, data)` implementation does:
   ```rust
   token::Client::new(&env, &wallet_token).transfer(&initiator, &attacker, &victim_balance);
   // then returns `amount_received` worth of collateral tokens to the controller
   // so the position passes `collect_collateral_deposits` minima and finalization
   ```
2. Victim (holding `WALLET_BALANCE` of an unrelated token, plus enough collateral) submits `flash_position` with `receiver = RogueReceiver`, `debt` = any flashloanable market, `collaterals` = a token the receiver will return.
3. Simulation records `token.transfer(victim, attacker, WALLET_BALANCE)` as a sub-invocation under the victim's `flash_position` entry — exactly as `rogue_hop_pool_transfer_joins_caller_auth_tree.rs` lines 206-222 show for the router path.
4. Victim signs the simulated tree; the transaction executes. Attacker's contract steals `WALLET_BALANCE` and still delivers the declared collateral, so `collect_collateral_deposits` (lines 325-352), `require_flash_position_still_open` (lines 356-370), and `strategy_finalize` all succeed — the call completes normally while the victim's wallet token is gone.

Root cause: `contracts/controller/src/strategies/flash_position.rs:308-322` invokes a fully caller-controlled contract address inside a transaction authorized by `require_authorized_caller` at line 45, injecting unvalidated user input into the privileged call stack — the same defect class as unsanitized `GIT_DIR` concatenated into `exec`'d command strings.