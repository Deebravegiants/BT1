### Title
Emporium's arbitrary `op.endpoint.call` can drain any ERC20 balance parked on the Emporium contract because `runAction`'s balance-accounting loop only covers attacker-chosen `circomData.erc20TokenAddresses` - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`EmporiumUpgradeable.runAction` lets a caller specify an arbitrary set of `EmporiumOperation`s (endpoint + callData) that are executed via raw `.call`, but the only economic check performed — the `balancesBefore`/`balancesAfter` diff — is computed strictly over `circomData.erc20TokenAddresses`, an array the attacker fully controls and can leave empty. Any ERC20 balance already sitting at the Emporium contract's address (a shared, non-per-user vault) for a token not listed in that array can therefore be moved out via a direct `token.transfer(attacker, balance)` call with zero on-chain accounting and, in the `signerAddress == address(0)` branch, with no signature check at all.

### Finding Description
The equality that is supposed to hold is:

`amount of any ERC20 token that leaves Emporium during runAction == sum of balanceChange entries reconciled in the erc20TokenAddresses loop (and represented by an output UTXO or relay payment)`

This equality is broken because the set of tokens Emporium's arbitrary calls can move is unconstrained, while the set of tokens accounted for is exactly `circomData.erc20TokenAddresses`, which is attacker-supplied calldata with no relationship enforced to the `ops` that are actually executed.

Concretely:
- `balancesBefore`/`balancesAfter` are computed with `getBalancesForArray(circomData.erc20TokenAddresses)` [1](#0-0)  and again after the ops run [2](#0-1) , and the reconciliation loop only iterates `circomData.erc20TokenAddresses.length` [3](#0-2) . If this array is empty, the loop body — including the `BalanceChangeShouldBePositive` guard and `handleOut` — never executes.
- The ops themselves are fully attacker-controlled: `EmporiumStack` is decoded straight from `circomData.externalActionData.externalActionMetadata` [4](#0-3) , and in the "Stateless Interaction" branch (`op.invokeWallet == false` or `stack.signerAddress == address(0)`), the only restriction is that the selector isn't `callHinkalWallet`/`doSendToRelay`; otherwise `op.endpoint.call{value: op.value}(op.callData)` executes verbatim [5](#0-4) .
- `verifyWallet` only performs signature/deadline checks when `stack.signerAddress != address(0)`; if the attacker sets `signerAddress = address(0)`, it returns immediately after marking `emporiumMessage` used, with no authorization check on the ops at all [6](#0-5) .
- `Hinkal.transact`'s own outer balance-diff/slippage checks are computed over the *same* attacker-supplied `circomData.erc20TokenAddresses` [7](#0-6) , so they provide no independent backstop — an omitted token is invisible at both layers.
- The ZK circuit/`performHinkalChecks`/`verifyProof` constrain the relationship between the attacker's own UTXOs and `amountChanges`/nullifiers for the declared token indices; they say nothing about tokens the attacker chooses not to declare, and do not constrain the semantics of `ops`/`externalActionMetadata` (that's the whole point of Emporium's generic call feature).

Exploit flow: attacker calls `Hinkal.transact` with a proof for their own UTXO(s), `dimensions` sized for a minimal circuit, `circomData.erc20TokenAddresses = []`, and `externalActionMetadata` encoding a single stateless `EmporiumOperation{ endpoint: token, invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attacker, balance)) }`. `runAction` executes the transfer, `balancesBefore`/`balancesAfter` are both zero-length arrays, `handleOut`/`BalanceChangeShouldBePositive` never run, and the stolen amount is never represented by an output UTXO or nullifier — it simply vanishes from Emporium's on-chain balance with no corresponding accounting anywhere in the protocol.

### Impact Explanation
Any ERC20 balance sitting at the Emporium contract address for a token not included in a subsequent `runAction`'s `erc20TokenAddresses` can be stolen outright by any unprivileged caller who can submit a `transact` with their own valid proof. Because Emporium is a single shared contract (not a per-user vault) and its ERC20 holdings are not tracked per-owner anywhere in `EmporiumStorage`, this is direct theft of funds that may belong to other users or to the protocol (e.g., residual token balances left behind by `handleOut`'s `balanceChange <= 0` skip path, by multi-step DeFi flows that intentionally park balances between calls, or by third-party token transfers/airdrops to the Emporium address). This matches the Critical category: direct theft of protocol/user-held funds, repeatable for every token balance that ever accumulates on Emporium.

### Likelihood Explanation
- Requires only that some ERC20 balance currently sits on the Emporium contract for a token the attacker's call declines to list — an entirely plausible and recurring state given `handleOut`'s explicit `balanceChange <= 0` skip-UTXO branch and any multi-step Emporium usage pattern where balances persist between calls.
- The attacker needs no privileged role: they only need to be an allowed Hinkal transactor with their own valid proof/UTXOs (which any user has by depositing their own funds).
- No signature is required when `stack.signerAddress == address(0)`, and `onlyAllowedRecipient` is satisfied automatically since `Hinkal` itself is the caller of `runAction`.
- The attack is repeatable every time Emporium accumulates an unlisted token balance.

### Recommendation
Do not let the reconciliation set be attacker-chosen independently of what the ops can touch. Options:
1. Require `circomData.erc20TokenAddresses` to include every token that could plausibly be affected by the declared `ops`/`externalActionMetadata` and enforce this via a proof-committed relationship (e.g., commit a hash of `externalActionMetadata` combined with the token list into the circuit's public inputs so the token set is provably complete for the ops executed).
2. Alternatively, track Emporium's ERC20 balances internally on a per-owner/per-message basis rather than relying purely on before/after global balance diffs restricted to an attacker-supplied array, so idle balances cannot be swept by unrelated callers.
3. At minimum, disallow arbitrary `op.endpoint.call` targets equal to `msg.sender`-held ERC20 tokens unless those tokens are present in `circomData.erc20TokenAddresses`, and revert if an op interacts with a token not declared in that array.

### Proof of Concept
Hardhat fork test plan:
1. Deploy `Hinkal`, `EmporiumUpgradeable` (as a registered external action), and a test ERC20.
2. Seed Emporium with a residual ERC20 balance by executing a legitimate `runAction` flow whose `handleOut` computes `balanceChange <= 0` for that token (or simply `transfer` tokens directly to the Emporium contract address to simulate "parked" balance, per the precondition already assumed valid in this class of finding).
3. As an unrelated attacker EOA, call `Hinkal.transact` with:
   - A valid proof over the attacker's own (possibly zero-value) UTXOs.
   - `circomData.erc20TokenAddresses = []`.
   - `circomData.externalActionData.externalActionMetadata` encoding an `EmporiumStack` with one stateless op: `endpoint = token`, `invokeWallet = false`, `value = 0`, `callData = abi.encodeCall(IERC20.transfer, (attacker, parkedBalance))`, `signerAddress = address(0)`.
4. Assert: token balance of Emporium decreases by `parkedBalance` and attacker's balance increases by the same amount, while `circomData.erc20TokenAddresses.length == 0` throughout `runAction`, and no `UTXO`/nullifier/commitment ever represents the stolen amount (confirming the two sides of the value-conservation equality — tokens actually moved vs. tokens accounted for in `balancesBefore`/`balancesAfter` — diverge by exactly `parkedBalance`).

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L80-83)
```text
        EmporiumStack memory stack = abi.decode(
            circomData.externalActionData.externalActionMetadata,
            (EmporiumStack)
        );
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-87)
```text
        uint256[] memory balancesBefore = getBalancesForArray(
            circomData.erc20TokenAddresses
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-124)
```text
        uint256[] memory balancesAfter = getBalancesForArray(
            circomData.erc20TokenAddresses
        );
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

**File:** contracts/Hinkal.sol (L78-147)
```text
            uint256[] memory oldBalances = getBalancesForArray(
                circomData.erc20TokenAddresses
            );

            if (circomData.externalActionData.externalActionId == 0) {
                _internalTransact(circomData);
            } else {
                utxoSet = _externalTransact(circomData);
            }

            uint256[] memory newBalances = getBalancesForArray(
                circomData.erc20TokenAddresses
            );

            OnChainCommitment[]
                memory onChainCommitments = new OnChainCommitment[](
                    utxoSet.length
                );
            uint256 onChainCommitmentCounter = 0;
            for (uint64 i; i < circomData.erc20TokenAddresses.length; i++) {
                int256 balanceDif;

                if (circomData.erc20TokenAddresses[i] == address(0)) {
                    balanceDif =
                        int256(newBalances[i]) +
                        int256(msg.value) -
                        int256(oldBalances[i]);
                } else {
                    balanceDif =
                        int256(newBalances[i]) -
                        int256(oldBalances[i]);
                }
                // balance inequality to check that minimum amount of token is received/given
                require(
                    balanceDif >= circomData.slippageValues[i],
                    "slippage param is violated"
                );

                uint256 utxoAmount = 0;
                for (uint j = 0; j < utxoSet.length; j++) {
                    if (
                        utxoSet[j].erc20Address ==
                        circomData.erc20TokenAddresses[i]
                    ) {
                        utxoAmount += utxoSet[j].amount;

                        onChainCommitments[
                            onChainCommitmentCounter
                        ] = createOnchainCommitment(
                            utxoSet[j],
                            circomData.onChainEncryptedOutput
                        );
                        onChainCommitmentCounter++;
                    }
                }

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
