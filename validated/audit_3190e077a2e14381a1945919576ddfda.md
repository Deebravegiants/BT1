### Title
Unrestricted `EmporiumOperation.endpoint`/`callData` in `EmporiumUpgradeable.runAction` lets an attacker plant a persistent ERC20 approval and drain any token balance the Emporium contract later holds - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction` executes attacker‑fully‑controlled `stack.ops` (stateless path) as raw `endpoint.call(callData)` from the Emporium contract's own address, with no allowlist on `endpoint` or `callData` content (only `callHinkalWallet`/`doSendToRelay` selectors are blocked). An attacker can encode an `approve(attacker, type(uint256).max)` call on any ERC20 token as one of the ops. The post-action balance-reconciliation logic only checks token *balances* before/after the call, never allowances, so the granted approval silently persists after the transaction completes and after `Hinkal.transact`'s balance/UTXO accounting closes out. In any later, completely separate transaction, the attacker can call `token.transferFrom(emporiumAddress, attacker, amount)` to steal whatever balance the Emporium contract is holding at that moment — including router refunds, dust, or another user's in-flight funds — bypassing Hinkal's accounting entirely.

### Finding Description
The invariant the question poses is: *tokens leaving the action in a tx == `-deltaAmountChanges` Hinkal sent it that tx*. `EmporiumUpgradeable.runAction` enforces this only for balance movements it can observe via `getBalancesForArray` deltas [1](#0-0) . It does not — and cannot — account for state changes that don't move balance immediately, such as ERC20 `approve` calls.

The root cause is in the stateless-operation branch of the ops loop: [2](#0-1) 
`op.endpoint` and `op.callData` come straight from `circomData.externalActionData.externalActionMetadata`, which is fully attacker-supplied (decoded via `abi.decode(...,(EmporiumStack))` with no validation) [3](#0-2) . The only selector-based restriction blocks calling back into the Hinkal wallet, not arbitrary ERC20 calls: [2](#0-1) . Since `stack.signerAddress` can be `address(0)`, `verifyWallet` requires no signature at all for this path [4](#0-3) , so an unprivileged caller of `Hinkal.transact` fully controls `op.endpoint`/`op.callData` with no counter-party signature needed.

Exploit flow:
1. Attacker calls `Hinkal.transact` with `externalActionId` pointing at the Emporium action, `externalActionMetadata` encoding an `EmporiumStack` with `signerAddress = address(0)` and one stateless op: `endpoint = <targetERC20>`, `callData = abi.encodeWithSelector(IERC20.approve.selector, attackerAddress, type(uint256).max)`.
2. `_externalTransact` in `Hinkal.sol` may or may not transfer any of the attacker's own funds into the Emporium depending on `deltaAmountChanges` [5](#0-4) ; the attacker can set their own `amountChanges`/`onChainCreation` (their own proof, own UTXOs) so this deposit is zero or trivial.
3. `runAction` executes the crafted op: `targetERC20.call(approve(attacker, max))`, executed with `msg.sender == EmporiumUpgradeable` inside the token contract, so the token contract records `allowance[EmporiumUpgradeable][attacker] = max`.
4. `balancesBefore`/`balancesAfter` for `targetERC20` are equal (no balance moved), so `balanceChange == 0`, `handleOut` returns an empty UTXO, and the top-level balance equation in `Hinkal.transact` (`balanceDif == amountChanges[i] + utxoAmount`) is trivially satisfied with zeros. Nothing in the invariant check ever inspects allowances, so this call passes every guard (`performHinkalChecks`, slippage check, balance-diff equality, `insertNullifiers`) cleanly.
5. The approval survives after the transaction. Any time afterward that the Emporium contract holds a balance of `targetERC20` — e.g., a router refund/residual left over from a swap in this or another user's action call (the "router refund leaves surplus output tokens parked in the action" scenario), dust from rounding, or tokens transferred in by `Hinkal._externalTransact` for a subsequent legitimate transaction just before its `runAction` executes — the attacker calls `targetERC20.transferFrom(EmporiumUpgradeable, attacker, amount)` directly, completely outside of `Hinkal.transact`, bypassing every Hinkal-side balance/UTXO/nullifier check.

This breaks the stated equality: tokens can leave the Emporium action's balance with `deltaAmountChanges == 0` for that transaction (the `transferFrom` transaction isn't a Hinkal transaction at all), meaning value leaves the action that Hinkal never authorized moving out.

None of the existing guards prevent this: `onlyAllowedRecipient` only restricts who can call `runAction` (must be Hinkal), not what `runAction` does internally [6](#0-5) ; `verifyWallet` only validates a signature when `signerAddress != address(0)`, which the attacker avoids [4](#0-3) ; the balance-diff equality in `Hinkal.transact` only checks balances, not allowances [7](#0-6) ; circuit constraints only bound `amountChanges`, not arbitrary contract-call side effects performed inside `runAction`.

### Impact Explanation
Critical — direct theft of shielded/in-flight user funds. Any balance the Emporium action contract holds at any point in time (residual router refunds, rounding dust from other users' swaps, or tokens transferred in by `Hinkal._externalTransact` for another user's transaction immediately before that transaction's `runAction` call executes) can be redirected to the attacker via a pre-planted `transferFrom` allowance. This is fully repeatable per-token and per-approval (the attacker can plant approvals for every token used by the Emporium action ahead of time, at near-zero cost, and simply monitor/drain balances as they appear).

### Likelihood Explanation
Low cost, high feasibility: the attacker only needs to be able to call `Hinkal.transact` for the Emporium action with a self-consistent proof over their own UTXOs (no deposit is even strictly required — `deltaAmountChanges` can be arranged to be zero/trivial), and craft `externalActionMetadata` with a stateless `EmporiumOperation` targeting an ERC20 `approve` call. No signature, no privileged role, and no interaction with any other party is required to plant the allowance. The only precondition for extracting value is that the Emporium contract at some later point holds a nonzero balance of the approved token, which is a realistic/likely occurrence given router refunds, slippage residues, and the multi-step transfer-then-runAction sequence in `Hinkal._externalTransact`.

### Recommendation
- Restrict `EmporiumOperation.endpoint` to an owner-managed allowlist of trusted router/DEX contracts, and/or disallow calling `approve`/`increaseAllowance`/other allowance-granting selectors on arbitrary tokens from within `runAction`'s stateless path.
- After executing all `ops`, revoke any approvals granted during the action (reset allowances for `circomData.erc20TokenAddresses` and any tokens touched by `ops` back to zero) before returning.
- Alternatively/additionally, sweep the Emporium contract's balance to zero (or to the computed UTXO output) for every token it can ever hold at the end of every `runAction` call so that no token balance is ever left resident in the contract between transactions, closing the "stranded balance" attack surface that the approval can later be used to steal.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `EmporiumUpgradeable` (registered as external action), a mock ERC20 `TKN`, and a mock "router" that simply forwards some `TKN` to `EmporiumUpgradeable` as a "refund" when called (simulating a residual/refund scenario), plus a valid Merkle/verifier test harness that lets the attacker submit real proofs over their own UTXOs (as used in existing repo tests).
2. Attacker tx #1: call `Hinkal.transact` for the Emporium action with `externalActionMetadata` encoding `EmporiumStack{signerAddress: address(0), ops: [{endpoint: TKN, invokeWallet: false, value: 0, callData: abi.encodeWithSelector(IERC20.approve.selector, attacker, type(uint256).max)}]}` and `deltaAmountChanges`/`amountChanges` set to 0 for `TKN`. Assert the transaction succeeds and `TKN.allowance(emporium, attacker) == type(uint256).max`.
3. Seed a residual balance: perform (or simulate) a second, unrelated legitimate action/refund that leaves `TKN.balanceOf(emporium) > 0` without it being swept out via `handleOut` (e.g., router refund exceeding what `balanceChange` captured, or a token transferred to Emporium outside the tracked `erc20TokenAddresses` array for that call).
4. Attacker tx #2 (fully independent, no Hinkal involvement): call `TKN.transferFrom(emporium, attacker, TKN.balanceOf(emporium))`.
5. Assertions on both sides of the invariant: before tx #2, `emporium.balanceOf(TKN) == R` (the residual) and no Hinkal transaction accounted for `R` leaving via `deltaAmountChanges`; after tx #2, `attacker.balanceOf(TKN) == R` and `emporium.balanceOf(TKN) == 0`, while `deltaAmountChanges` recorded by Hinkal for that transferred amount is `0` — proving tokens left the action without any corresponding `-deltaAmountChanges` Hinkal accounting.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L80-83)
```text
        EmporiumStack memory stack = abi.decode(
            circomData.externalActionData.externalActionMetadata,
            (EmporiumStack)
        );
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L102-113)
```text
            // CASE 2: Stateless Interaction
            else {
                bytes4 selector = bytes4(op.callData);
                if (
                    selector == IHinkalWallet.callHinkalWallet.selector ||
                    selector == IHinkalWallet.doSendToRelay.selector
                ) {
                    revert UnauthorizedWalletCall();
                }

                (success, err) = op.endpoint.call{value: op.value}(op.callData);
            }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-151)
```text
        uint256[] memory balancesAfter = getBalancesForArray(
            circomData.erc20TokenAddresses
        );

        UTXO[] memory utxoSet = new UTXO[](
            circomData.erc20TokenAddresses.length
        );

        uint256 utxoSetLength;

        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            int256 balanceChange = int256(balancesAfter[i]) -
                int256(balancesBefore[i]);

            if (deltaAmountChanges[i] < 0) {
                balanceChange -= deltaAmountChanges[i];
                // this equation reads: total change of emporium balance = what was moved to emporium (-deltaAmountChange) + how emporium balance changed through tx (balanceChange)
            }

            // the only case when balanceChange can be < 0, when there were some funds on emporium before the call
            if (balanceChange < 0) {
                revert BalanceChangeShouldBePositive();
            }

            UTXO memory utxoOut = handleOut(balanceChange, circomData, i);

            if (utxoOut.amount > 0) {
                utxoSet[utxoSetLength++] = utxoOut;
            }
        }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L313-317)
```text

        if (stack.signerAddress == address(0)) {
            return;
        }

```

**File:** contracts/Hinkal.sol (L134-147)
```text
                // balance equation to check: CHANGE IN BALANCE SHOULD EQUAL TO
                // 1) change in off-chain utxos
                // 2) change in on-chain utxos
                require(
                    balanceDif ==
                        (
                            circomData.onChainCreation[i]
                                ? int256(0)
                                : circomData.amountChanges[i]
                        ) +
                            int256(utxoAmount),
                    "Balance Diff Should be equal to sum of onchain and offchain created commitments"
                );
            }
```

**File:** contracts/Hinkal.sol (L244-256)
```text
        int256[] memory deltaAmountChanges = new int256[](
            circomData.erc20TokenAddresses.length
        );
        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            deltaAmountChanges[i] = _calculateDeltaAmount(circomData, i);
            if (deltaAmountChanges[i] < 0) {
                transferERC20TokenOrETH(
                    circomData.erc20TokenAddresses[i],
                    circomData.externalActionData.externalAddress,
                    uint256(-deltaAmountChanges[i])
                );
            }
        }
```

**File:** contracts/external-actions/ExternalActionBaseUpgradeable.sol (L39-46)
```text
    modifier onlyAllowedRecipient() {
        ExternalActionBaseStorage storage $ = _getExternalActionBaseStorage();
        require(
            $._isAllowedRecipient[msg.sender],
            "ExternalActionBase: sender not allowed"
        );
        _;
    }
```
