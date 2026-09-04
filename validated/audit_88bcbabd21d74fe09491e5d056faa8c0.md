### Title
Unaccounted ERC20 sweep via attacker-controlled `EmporiumOperation` bypasses balance-delta check - (contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol :: EmporiumUpgradeable.runAction)

### Summary
`EmporiumUpgradeable.runAction` only snapshots and checks balances for the tokens listed in `circomData.erc20TokenAddresses`, but the `stack.ops` executed in between (fully attacker-controlled when `stack.signerAddress == address(0)`) can call `transfer`/withdrawal logic on **any** token contract, not just the ones in that array. Any value already sitting in the Emporium/HinkalWallet contract for a token that is *not* included in the caller's `erc20TokenAddresses` list can be swept to the attacker with no balance check and no revert.

### Finding Description
The invariant the audit question asks us to verify is: *tokens leaving the action in a tx == -deltaAmountChanges Hinkal sent it that tx*. In `EmporiumUpgradeable.runAction` this is enforced only for the subset of tokens present in `circomData.erc20TokenAddresses`: [1](#0-0) 

`balancesBefore`/`balancesAfter` are only computed for that array, and the only guard against value leaving the action uncounted is: [2](#0-1) 

which reverts with `BalanceChangeShouldBePositive` **only** for tokens in `erc20TokenAddresses`. The `stack.ops` loop that executes in between, however, is not restricted to those tokens at all: [3](#0-2) 

For `stack.signerAddress == address(0)` (the "self" execution mode), `verifyWallet` performs **no** signature check at all and simply marks the message as used: [4](#0-3) 

This means the attacker fully controls `stack.ops[i].endpoint` / `callData` for their own transaction. The only blocked selectors are `callHinkalWallet` and `doSendToRelay`: [5](#0-4) 

So an attacker can include an op whose `endpoint` is an arbitrary ERC20 token address `T` that the Emporium/HinkalWallet contract happens to hold a balance of (residual/stranded from a prior action's swap dust, an over-swap remainder, a partially-processed multi-op action, etc.), with `callData = transfer(attacker, T.balanceOf(emporium))`. As long as `T` is **not** included in `circomData.erc20TokenAddresses` for this transaction, `balancesBefore`/`balancesAfter` never observe `T`, the `balanceChange < 0` guard is never evaluated for it, and the drained value never has to reconcile against any `deltaAmountChanges` entry. The circuit only constrains `inTotal + amountChanges === outTotal` for the tokens the prover chose to declare in `erc20TokenAddresses`/`amountChanges` - it has no knowledge of, and places no constraint on, what other tokens the `ops` payload touches. `handleOut` and the SNARK's internal balancing therefore never see this transfer, so it is stolen entirely outside of the audited equality.

### Impact Explanation
Any ERC20 (or ETH, via `op.value`) balance parked in the Emporium/HinkalWallet contract that is not part of the attacker's declared `erc20TokenAddresses` array for that call can be swept to the attacker's own address, with zero relationship to their own `deltaAmountChanges`. If that stranded balance originates from another user's prior action (e.g., dust left behind after a swap because the output token differed from what was declared, or a partially failed multi-op sequence), this is direct theft of another party's in-flight/protocol funds routed through the Hinkal Emporium action - matching the Critical "direct theft of shielded or in-flight user funds" category. It is repeatable any time residual balance exists in the contract, and costs the attacker only the price of submitting a valid Hinkal proof for an unrelated/zero-value token set.

### Likelihood Explanation
Exploitability requires that some stranded balance already exists for a token in the Emporium/HinkalWallet contract that is not part of the attacker's own declared token list - this is not always guaranteed to exist, so likelihood depends on operational conditions (dust from prior swaps/actions, partial multi-op failures, etc.) rather than being unconditionally triggerable on a clean contract. When such residual exists, exploitation is trivial and cheap: the attacker needs only a valid self-authored proof (no signer signature required, since `signerAddress == address(0)` skips `verifyWallet`'s authorization check) and an `EmporiumOperation` targeting the stranded token's `transfer` function.

### Recommendation
Enforce that every `stack.ops[i].endpoint` interacting with a token balance is restricted to tokens included in `circomData.erc20TokenAddresses` (or otherwise snapshot/verify balances for the full set of addresses touched by `ops`, not just the caller-declared array), and/or require that after all ops execute, the contract's balance for *every* token it holds (not merely the declared subset) is reconciled so no value can leave undetected. Alternatively, sweep any pre-existing balance for undeclared tokens back into the shielded pool automatically before allowing `ops` to execute, so stranded residuals cannot be captured by omission.

### Proof of Concept
Foundry plan:
1. Deploy `EmporiumUpgradeable` (or its proxy) with a `HinkalHelper` stub and an allowed-recipient `Hinkal` mock.
2. Seed a "stranded" residual: mint token `T` directly to the Emporium contract address (simulating leftover dust from a prior action) without it appearing in any `erc20TokenAddresses` array for the next call.
3. As an unprivileged attacker, construct `CircomData` with `erc20TokenAddresses = [otherToken]` (unrelated to `T`), valid nullifiers/roots for the attacker's own dummy UTXO, `externalActionData.externalActionMetadata` ABI-encoding an `EmporiumStack` with `signerAddress = address(0)` and `ops = [{endpoint: T, invokeWallet: false, value: 0, callData: abi.encodeWithSelector(IERC20.transfer.selector, attacker, T.balanceOf(emporium))}]`.
4. Call `Hinkal.transact` (or directly `EmporiumUpgradeable.runAction` if allowed-recipient) with this payload.
5. Assert: (a) call does not revert with `BalanceChangeShouldBePositive`; (b) `T.balanceOf(attacker)` increases by the full stranded amount; (c) no `deltaAmountChanges` entry accounts for token `T`, proving the equality "tokens leaving the action == -deltaAmountChanges Hinkal sent it" is broken for `T`.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-90)
```text
        uint256[] memory balancesBefore = getBalancesForArray(
            circomData.erc20TokenAddresses
        );

        verifyWallet(stack, circomData);

```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L91-118)
```text
        for (uint256 i = 0; i < stack.ops.length; i++) {
            EmporiumOperation memory op = stack.ops[i];

            bool success;
            bytes memory err;

            // CASE 1: Stateful Interaction
            if (op.invokeWallet && stack.signerAddress != address(0)) {
                (success, err) = IHinkalWallet(stack.signerAddress)
                    .callHinkalWallet(op.endpoint, op.callData, op.value);
            }
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

            if (!success) {
                revert CallFailed(err);
            }
        }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L132-151)
```text
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-316)
```text
    function verifyWallet(
        EmporiumStack memory stack,
        CircomData calldata circomData
    ) internal {
        EmporiumStorageVars storage $ = _getEmporiumStorage();

        if ($.usedMessages[circomData.emporiumMessage]) {
            revert UsedMessage();
        }

        $.usedMessages[circomData.emporiumMessage] = true;

        if (stack.signerAddress == address(0)) {
            return;
        }
```
