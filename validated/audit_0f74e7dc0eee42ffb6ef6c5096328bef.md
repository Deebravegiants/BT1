Based on my investigation of `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`, here is my finding.

### Title
Emporium ops execute arbitrary calls that can sweep any ERC20 balance held by the action to an attacker, bypassing the per-token balance invariant when the target token is omitted from `erc20TokenAddresses` - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction` executes attacker-supplied `ops` with no restriction on which contracts/tokens they can call, and only checks the pre/post balance delta for tokens explicitly listed in `circomData.erc20TokenAddresses`. When `stack.signerAddress == address(0)`, `verifyWallet` skips all signature checks entirely, so an unprivileged attacker fully controls `op.endpoint`/`op.callData`. An attacker can craft an op that calls `token.transfer(attacker, balance)` directly from the Emporium contract's own context, while simply excluding that `token` from `circomData.erc20TokenAddresses`, so the theft is never reflected in the `balanceChange`/`deltaAmountChanges` reconciliation.

### Finding Description
The invariant the code intends to enforce is: for every token index `i` in `circomData.erc20TokenAddresses`, `balancesAfter[i] - balancesBefore[i] + (deltaAmountChanges[i]<0 ? -deltaAmountChanges[i] : 0) >= 0`, i.e. tokens leaving the action equal `-deltaAmountChanges` plus whatever the ops legitimately produced [1](#0-0) .

This invariant is only checked per-index over `circomData.erc20TokenAddresses` — an array fully chosen by the attacker/prover. The `ops` loop, however, is not scoped to those tokens at all: [2](#0-1) 

When `stack.signerAddress == address(0)` (stateless case), `verifyWallet` returns immediately without any signature check on `stack.ops`: [3](#0-2) 

Since `stack` is decoded straight from `circomData.externalActionData.externalActionMetadata`, which is entirely attacker-supplied calldata for their own transaction, the attacker can set `op.endpoint = <any ERC20 token that the Emporium contract currently holds a balance of>` and `op.callData = abi.encodeWithSelector(IERC20.transfer.selector, attacker, amount)`. The only checks on `op.callData` are that its selector isn't `callHinkalWallet`/`doSendToRelay`; any other selector, including a raw ERC20 `transfer`, is permitted [4](#0-3) . Because the call is `op.endpoint.call(...)` issued from inside `EmporiumUpgradeable`, `msg.sender` seen by the token is the Emporium contract, so `transfer` moves the Emporium's own balance to the attacker.

The stolen `token` need not appear anywhere in `circomData.erc20TokenAddresses` for this particular transaction. As long as it's absent from that array, `balancesBefore`/`balancesAfter` are never computed for it, so the `balanceChange < 0` revert guard (`BalanceChangeShouldBePositive`) never triggers for the stolen token, and `handleOut` never has a chance to detect the drain.

This exact vector applies to the described scenario: relay fees that were supposed to be paid via `payRelayFees`/`payRelay` are silently *not* transferred when `circomData.relay == address(0)` [5](#0-4) , leaving that fee amount sitting as a real ERC20 balance on the Emporium contract from a prior, legitimate transaction. Any subsequent unprivileged caller can then run a new Emporium action whose `ops` sweep that stranded balance directly to themselves, without ever declaring the fee token in `erc20TokenAddresses`, defeating the "tokens leaving == -deltaAmountChanges" invariant entirely.

I was not able to fully verify whether `dimensionsCheck` or the circuit's public-input constraints (`calldataHash`, etc., referenced in `MainEVMCircuit.circom`/`HinkalHelper.sol`) impose any binding between `externalActionMetadata` (and thus `ops`) and `erc20TokenAddresses` that would restrict which tokens an op can target. My searches surfaced references to `calldataHash`/`dimensionsCheck` in `HinkalHelper.sol` and the circuit files but I could not confirm their exact semantics within the available iterations — this is the main residual uncertainty in this analysis.

### Impact Explanation
An attacker can drain any ERC20 balance currently held by the `EmporiumUpgradeable` contract that is not their own accounted deposit for that transaction — including stranded relay fees, and potentially in-flight funds belonging to other users' pending multi-step Emporium operations. This is direct theft of protocol/relay fees and potentially of user funds sitting transiently in the action, matching the Critical/High impact categories in scope.

### Likelihood Explanation
Preconditions: some ERC20 balance must be sitting in the Emporium contract (e.g., stranded relay fee from a `relay == address(0)` transaction, or residual dust from any prior operation). The attacker needs no special role — just the ability to submit their own `Hinkal.transact` call with `stack.signerAddress == address(0)` and craft `ops` and `erc20TokenAddresses` themselves. This is fully within the "unprivileged attacker" capability set described in the rules. Repeatable any time such a balance exists.

### Recommendation
Restrict `op.endpoint` calls (at minimum in the stateless/no-signer branch) from targeting arbitrary token contracts outside of `circomData.erc20TokenAddresses`, or require that any token balance touched by `ops` be included and reconciled in the `erc20TokenAddresses` balance-check loop. Alternatively, snapshot and verify balances for *all* tokens the Emporium contract could plausibly hold (or maintain a contract-level whitelist/allowance model for `ops` calls) rather than relying on the attacker-chosen `erc20TokenAddresses` array to define what gets checked.

### Proof of Concept
1. Deploy `EmporiumUpgradeable`, seed it with a stranded ERC20 balance by running one legitimate Emporium action with `circomData.relay == address(0)` and a nonzero `feeStructure.flatFee`, confirming the fee token remains in the Emporium contract instead of being paid out (via `payRelay`'s early return).
2. As a second, unrelated unprivileged attacker EOA, craft a new `Hinkal.transact` call with a locally generated proof for their own UTXOs, `circomData.erc20TokenAddresses` that does **not** include the stranded fee token, and `externalActionMetadata` encoding an `EmporiumStack` with `signerAddress == address(0)` and one `op` = `{ endpoint: feeToken, callData: abi.encodeWithSelector(IERC20.transfer.selector, attacker, strandedAmount), value: 0 }`.
3. Assert before/after: `strandedAmount` moves from the Emporium contract to the attacker's EOA, while `sum(deltaAmountChanges)` for the attacker's declared tokens in that transaction accounts for none of it — i.e. `tokens leaving action == -deltaAmountChanges Hinkal sent it` is violated for the fee token.

### Citations

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L262-282)
```text
    function payRelay(
        address relay,
        address signerAddress,
        uint256 relayFee,
        address erc20TokenAddress
    ) internal {
        if (relay == address(0) || relayFee == 0) {
            return;
        }

        if (signerAddress == address(0)) {
            sendToRelay(relay, relayFee, erc20TokenAddress);
        } else {
            sendToRelayFromWallet(
                relay,
                signerAddress,
                relayFee,
                erc20TokenAddress
            );
        }
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-317)
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
