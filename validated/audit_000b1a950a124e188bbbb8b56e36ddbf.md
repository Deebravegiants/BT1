### Title
Emporium's stateless op calls can drain any ERC20/ETH token held by the Emporium contract that the attacker omits from `circomData.erc20TokenAddresses` - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.runAction()` only checks a balance-conservation equation for the tokens listed in `circomData.erc20TokenAddresses`. Any unprivileged user who submits a valid `transact()` proof for their own (arbitrary, even dust-sized) shielded UTXOs can attach an `EmporiumStack` whose "Stateless Interaction" op (`op.endpoint.call(op.callData)`) is executed with `msg.sender == Emporium`. Because that op's target token and recipient are fully attacker-controlled and are never required to be included in `circomData.erc20TokenAddresses`, an attacker can direct a `transfer(attacker, amount)` call on any ERC20 token the Emporium contract currently holds (e.g. protocol fee residue, swap dust, tokens left over from other users' external actions) straight to their own wallet, completely outside the balance equation that is supposed to bound value movement.

### Finding Description
`Hinkal.transact()` verifies the ZK proof and root, then delegates to `_externalTransact()` → `IExternalActionV2(externalAddress).runAction(circomData, deltaAmountChanges)`. [1](#0-0) 

Inside `EmporiumUpgradeable.runAction()`, the "Stateless Interaction" branch performs an unrestricted low-level call from the Emporium contract's own context: [2](#0-1) 

The only post-call accounting is a before/after balance-delta check limited strictly to `circomData.erc20TokenAddresses`: [3](#0-2) 

Crucially, `stack.ops` (containing `endpoint`, `callData`, `value`) come from `circomData.externalActionData.externalActionMetadata`, and are only signature-checked via `verifyWallet` when `stack.signerAddress != address(0)`. When `signerAddress == address(0)`, `verifyWallet` returns immediately after marking the message used, performing **no signature check on the ops at all**: [4](#0-3) 

The Solidity comment itself acknowledges that Emporium can retain balance between transactions ("the only case when balanceChange can be < 0, when there were some funds on emporium before the call"), confirming the contract is a shared pool across all users' external actions and can accumulate residual token balances (fee dust, partial swap leftovers, previous unclaimed positive deltas, etc.). [5](#0-4) 

Because `circomData.erc20TokenAddresses` is chosen entirely by the caller (only checked by the circuit/`dimensionsCheck` for length/consistency and distinctness among themselves, not for completeness against what the embedded `callData` actually touches), an attacker can simply exclude a token that Emporium already holds from that array. The op then calls `Token.transfer(attackerEOA, balance)` directly. Since that token's balance is untracked by the `for` loop in `runAction` (it never appears in `erc20TokenAddresses`), no `balanceChange` check, slippage check, or UTXO/nullifier accounting touches it whatsoever — the value transfer happens completely outside the equality:
`balanceDif == amountChanges[i] + utxoAmount`
established in `Hinkal.sol`: [6](#0-5) 

This is the direct analog of the KelpDAO issue: just as `getTotalAssetDeposits()` silently dropped the old-strategy balance from its accounting (a value that existed but fell outside the checked set), here any token balance sitting in Emporium but excluded from the attacker-chosen `erc20TokenAddresses` array falls outside the checked set and can be moved with zero accounting.

### Impact Explanation
This is a direct theft primitive against protocol/relay fee residue and any other tokens the shared Emporium contract holds (High/Critical depending on what accumulates there in practice) — funds are moved out of the protocol to an unauthorized recipient (the attacker's raw EOA) with no nullifier spent, no UTXO created, and no balance check performed, i.e. unauthorized asset movement bypassing the balance equation entirely.

### Likelihood Explanation
Any unprivileged EOA holding even a trivial valid shielded balance can trigger this: they only need one legitimate small deposit to generate a valid proof for `transact()` with `externalActionId` pointing at Emporium, then craft `externalActionMetadata` with `signerAddress = address(0)` (bypassing the EIP-712 signature entirely) and an op whose `callData` transfers an arbitrary, unlisted token held by Emporium to themselves. The only precondition is that Emporium actually holds a non-zero balance of some token not listed by the attacker — plausible given the contract's own comment about carrying balances between calls, and given relay/fee flows and multi-hop swap dust that can accumulate there over the protocol's lifetime.

### Recommendation
Enforce that all tokens/ETH that could be affected by `stack.ops` calls are declared in `circomData.erc20TokenAddresses` and are the only assets the ops are permitted to touch (e.g., restrict callable selectors/targets to a pre-approved allowlist, or snapshot and diff the balances of *all* addressable assets, not just the caller-declared subset). Alternatively, require `stack.ops` to always be authorized via a real signer (disallow the `signerAddress == address(0)` bypass for stateless calls), and additionally sweep/zero out any Emporium residual balance to a designated treasury after each `runAction` so that no value can silently accumulate and later be drained by an unrelated caller.

### Proof of Concept
1. Assume Emporium currently holds `100` units of token `Y` (e.g., accumulated dust from a prior unrelated user's swap op, or fee residue that was never swept because it wasn't listed in that transaction's `erc20TokenAddresses`).
2. Attacker (holding any legitimate shielded UTXO, even for an unrelated token `X`) constructs a valid `transact()` call with `externalActionData.externalActionId` pointing at Emporium and `erc20TokenAddresses = [X]` only (token `Y` is deliberately omitted).
3. Attacker sets `externalActionData.externalActionMetadata` to an `EmporiumStack` with `signerAddress = address(0)` and one stateless op: `{ endpoint: Y, invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attackerEOA, 100)) }`.
4. `verifyWallet` performs no signature check because `signerAddress == address(0)` (only marks `emporiumMessage` as used).
5. `runAction` executes `Y.call(callData)` from Emporium's context, transferring the 100 units of `Y` directly to `attackerEOA`.
6. The post-call balance check loop in `runAction`/`Hinkal.sol` only iterates over `[X]`; token `Y`'s balance change is never inspected, so no revert occurs and no nullifier/UTXO accounting reflects the stolen `Y` tokens.
7. Attacker walks away with `100 Y` for the cost of a normal-fee transaction on their own unrelated `X` balance.

### Citations

**File:** contracts/Hinkal.sol (L82-86)
```text
            if (circomData.externalActionData.externalActionId == 0) {
                _internalTransact(circomData);
            } else {
                utxoSet = _externalTransact(circomData);
            }
```

**File:** contracts/Hinkal.sol (L134-146)
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
