### Title
Unauthenticated `EmporiumStack` with `signerAddress = address(0)` allows arbitrary `endpoint.call` as the Emporium contract, enabling theft of any ERC20 allowance granted to Emporium - (`contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.runAction` decodes an attacker-supplied `EmporiumStack` from `circomData.externalActionData.externalActionMetadata` and executes every `EmporiumOperation` in it. When the attacker sets `stack.signerAddress = address(0)`, `verifyWallet` returns immediately with **no signature check at all**, and the op-dispatch logic (`op.invokeWallet && stack.signerAddress != address(0)`) forces every op into the "stateless" branch that executes `op.endpoint.call{value: op.value}(op.callData)` directly from the Emporium contract's own context. This lets an attacker make Emporium call `ERC20.transferFrom(victim, attacker, amount)` on any token where a victim has left a standing allowance to the Emporium contract address.

### Finding Description
Broken equality: **AUTHORITY** — the `from` address of the stolen `transferFrom` was never proven by, or tied to, the ZK proof/EIP-712 signer for this transaction; **VALUE CONSERVATION** — `deltaAmountChanges[i]` for the stolen token is `0` (or unrelated), yet `balanceChange`/minted UTXO for that token index is positive, funded entirely by a third party's allowance.

Code path:
1. `Hinkal._externalTransact` (contracts/Hinkal.sol:234-261) only moves funds for `deltaAmountChanges[i] < 0`; it never validates what the external action does internally, and calls `IExternalActionV2(externalAddress).runAction(circomData, deltaAmountChanges)`.
2. `EmporiumUpgradeable.runAction` (contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol:76-160) decodes the attacker-controlled `EmporiumStack` and calls `verifyWallet(stack, circomData)`.
3. `verifyWallet` (same file, lines 302-316) skips ALL EIP-712 signature verification when `stack.signerAddress == address(0)`, only marking the `emporiumMessage` nonce used.
4. In the ops loop (lines 91-118), the branch condition `op.invokeWallet && stack.signerAddress != address(0)` is false whenever `signerAddress == address(0)`, regardless of `op.invokeWallet`. Every op therefore falls into "CASE 2: Stateless Interaction" (lines 102-113), which only blocks the `callHinkalWallet`/`doSendToRelay` selectors and then executes `op.endpoint.call{value: op.value}(op.callData)` with `msg.sender == address(EmporiumUpgradeable)`.
5. An attacker sets `op.endpoint = TOKEN` and `op.callData = abi.encodeWithSelector(IERC20.transferFrom.selector, victim, recipient, amount)`. Since the call originates from the Emporium contract, this succeeds if `TOKEN.allowance(victim, address(Emporium)) >= amount` — regardless of who `victim` is.
6. After the ops loop, `balancesAfter - balancesBefore` for `TOKEN` includes the stolen amount; since `deltaAmountChanges[i]` for that token is unrelated/zero, `handleOut` (lines 162-184) mints the attacker a UTXO for the full stolen `balanceChange` and transfers the tokens to `msg.sender` (the attacker).

No existing guard prevents this: `performHinkalChecks`/`verifyProof` only validate the attacker's own proof over their own nullifiers/commitments; they say nothing about arbitrary `op.callData`. `onlyAllowedRecipient` only restricts who may call `runAction` (i.e., the registered Hinkal contract), not what the decoded ops may do. The selector blocklist in CASE 2 only excludes `IHinkalWallet` selectors, not arbitrary ERC20 `transferFrom` calls.

### Impact Explanation
Any ERC20 allowance a victim has ever granted to the shared Emporium contract address (e.g., left over from a prior deposit using the "self-relay"/`signerAddress==0` stateless deposit pattern, or an unlimited/standing approval for UX convenience) can be drained by any unprivileged attacker in a single transaction. This is direct theft of third-party funds having nothing to do with the attacker's own proof or shielded balance — matching the Critical severity category (direct theft of user funds via an action never authorized by the wallet owner/prover).

### Likelihood Explanation
Preconditions: a victim must have a nonzero ERC20 allowance outstanding to the Emporium contract address for some token. This is a realistic condition because the "stateless"/`signerAddress==0` op path is the documented mechanism for a user to deposit tokens into Emporium by including a `transferFrom(self, Emporium, amount)` op directly (self-authorizing via being `msg.sender` of the outer `transact` call) — a design that naturally encourages standing/unlimited approvals to the Emporium contract for UX efficiency. The attacker's cost is only their own gas plus a valid proof over their own (even zero-value) UTXOs; no special privilege, victim cooperation, or timing race is required beyond an existing nonzero allowance, and the attack is repeatable per victim/token/allowance.

### Recommendation
Do not allow arbitrary stateless calls to make Emporium the `msg.sender` for third-party-controlled tokens. Specifically:
- Require every op's `callData` to be authenticated by the same EIP-712 signature/HinkalWallet indirection regardless of `signerAddress`, i.e., disallow the "no-signature" branch from executing arbitrary calldata against arbitrary endpoints.
- Alternatively, restrict stateless (non-wallet) ops so that they can never call a function whose first argument (`from`) could be interpreted as pulling funds from anyone other than `msg.sender` of the outer transaction (e.g., disallow raw `transferFrom`/`approve`-style selectors entirely in the unauthenticated path, or enforce an allowlist of safe endpoints for `signerAddress == address(0)`).
- Bind the decoded `EmporiumStack.ops` cryptographically to `msg.sender` (the outer transact caller) when `signerAddress == address(0)`, so the "self-relay" path can only move the caller's own previously-approved funds.

### Proof of Concept
Foundry test outline:
1. Deploy `Hinkal`, `EmporiumUpgradeable` (as a registered external action), and a mock ERC20 `TOKEN`.
2. `victim` calls `TOKEN.approve(address(emporium), 1000e18)` directly (simulating a standing/leftover approval from a prior stateless deposit), outside of any Hinkal transaction.
3. `attacker` generates a valid proof for their own (even zero-amount) UTXO set with `erc20TokenAddresses = [TOKEN]`, `amountChanges[0] == 0`/`deltaAmountChanges[0] == 0`.
4. `attacker` encodes `externalActionMetadata` as an `EmporiumStack{ signerAddress: address(0), ops: [ { endpoint: TOKEN, invokeWallet: false, value: 0, callData: abi.encodeWithSelector(IERC20.transferFrom.selector, victim, attacker, 1000e18) } ] }`.
5. Call `Hinkal.transact(a, b, c, dimensions, circomData)` from `attacker`.
6. Assert: `TOKEN.balanceOf(victim)` decreased by `1000e18`, `TOKEN.balanceOf(attacker)` increased by `1000e18`, and a new UTXO for `attacker` with `amount == 1000e18` for `TOKEN` was emitted/inserted — while `circomData.amountChanges[0] == 0` (i.e., the attacker contributed nothing for that token in this transaction).