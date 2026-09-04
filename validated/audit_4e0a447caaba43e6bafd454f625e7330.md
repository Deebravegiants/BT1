### Title
Empty `erc20TokenAddresses` vacuously satisfies value conservation while `EmporiumUpgradeable.runAction`'s `ops` loop still executes arbitrary calls — ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`EmporiumUpgradeable.runAction` executes `stack.ops` (arbitrary attacker-crafted calls, including `op.endpoint.call{value: op.value}(op.callData)`) in a loop that is completely independent of `circomData.erc20TokenAddresses`. The subsequent accounting loop that calls `handleOut` and the parent `Hinkal.transact` conservation check both iterate strictly `for (i = 0; i < erc20TokenAddresses.length; i++)`. If the attacker sets `erc20TokenAddresses = []`, both accounting loops execute zero times, so the value-conservation equality is checked against nothing while the `ops` loop still runs and can move any ETH/ERC20 that Emporium holds.

### Finding Description
The claimed equality is:

`sum(tokens actually moved out of Emporium during ops execution) == sum(-deltaAmountChanges[i] over i captured in utxoSet)`

Trace:
- `EmporiumUpgradeable.runAction` (lines 91-118) executes `stack.ops[i].endpoint.call{value: op.value}(op.callData)` or `IHinkalWallet.callHinkalWallet(...)` for every op in `stack.ops`, decoded from attacker-controlled `circomData.externalActionData.externalActionMetadata`. This loop has **no dependency whatsoever** on `circomData.erc20TokenAddresses`. [1](#0-0) 
- Balance accounting only happens afterwards, over `circomData.erc20TokenAddresses`: [2](#0-1) 
- `handleOut` is only ever invoked from inside that same bounded loop (line 146), so with `erc20TokenAddresses = []` it is never called, and `utxoSet` stays empty. [3](#0-2) 
- Back in `Hinkal.transact`, the global value-conservation invariant is likewise gated by the same array's length: [4](#0-3) 
With `circomData.erc20TokenAddresses.length == 0`, this `for` loop body — containing the `balanceDif ==  amountChanges[i] + utxoAmount` `require` — never executes. The equality is not "checked and found equal"; it is simply never evaluated, i.e. vacuously satisfied (`0` iterations, `0 == 0` by omission, not by actual balance equality).
- `deltaAmountChanges` passed into `runAction` is also sized to `erc20TokenAddresses.length`, so it is `[]` too: [5](#0-4) 

Root cause: the code assumes `erc20TokenAddresses` is an exhaustive list of every asset an external action can touch, and enforces conservation only over that attacker-supplied list, while the actual arbitrary-call execution surface (`stack.ops`) is unconstrained by that same list.

None of the listed guards close this gap: `performHinkalChecks`/`dimensionsCheck` validate proof structure and dimension consistency but do not force `erc20TokenAddresses` to be non-empty or to include every token touched by `ops`; `verifyProof`/circuit constraints (`inTotal + amountChanges === outTotal`) operate purely on the circuit's public inputs for the tokens actually listed — an empty list means the circuit-side conservation is likewise vacuous for those unlisted assets; `insertNullifiers`/`rootHashExists` govern the shielded-input side, not funds extracted via arbitrary `ops` calls; `nonReentrant` prevents reentrancy, not this accounting bypass; `onlyAllowedRecipient` only gates who may call `runAction` (must be the registered Hinkal contract), not what `stack.ops` may contain.

### Impact Explanation
Any asset balance held by the `EmporiumUpgradeable` contract that is not enumerated in `erc20TokenAddresses` for a given `transact()` call can be moved out via `ops` without being recorded as a `UTXO`, without appearing in `utxoSet`, and without triggering the `balanceDif` equality check in `Hinkal.transact`. This breaks Hinkal's core invariant that all value entering/leaving an external action is accounted for by shielded UTXOs or explicit nullifier/commitment bookkeeping — a Critical-severity direct value-extraction/accounting-bypass condition, matching the "direct theft of shielded or in-flight user funds" category if Emporium holds any residual/in-flight balance belonging to the protocol or other users (e.g., dust left over from prior swaps/operations, or funds routed through Emporium in a multi-step flow). It is repeatable on every transaction where the attacker chooses an empty `erc20TokenAddresses` array and Emporium holds extractable balance.

### Likelihood Explanation
The attacker fully controls `circomData.erc20TokenAddresses` (can set it to `[]`), `circomData.externalActionData.externalActionMetadata` (decoded as `stack.ops`, including arbitrary `endpoint`/`callData`/`value`), and can supply their own valid proof for a `circomData` with zero token entries (the `dimensionsCheck` and circuit constraints for an empty token array are trivially satisfiable). The only external precondition is that Emporium hold some extractable balance (ETH or ERC20) at call time — plausible given Emporium's `receive()` function is unguarded and its balance persists across transactions/users, and given that other legitimate flows route funds through it. Attacker cost is a single `transact()` call; the bypass is not gas-griefing or DoS, it is a direct accounting omission.

### Recommendation
Do not let `erc20TokenAddresses` be attacker-selectable independently of what `stack.ops` can touch. Either:
1. Require `circomData.erc20TokenAddresses` to be non-empty and derived/validated against the actual token set involved in `stack.ops` (e.g., statically declared and checked at commit time), or
2. Snapshot and diff Emporium's *total* balance for every asset it could conceivably hold (or restrict `ops.endpoint`/`callData` to a whitelist that cannot move untracked assets) before/after the `ops` loop regardless of `erc20TokenAddresses.length`, reverting if any balance change is detected for a token not present in `erc20TokenAddresses`.
3. At minimum, revert `runAction` if `erc20TokenAddresses.length == 0` while `stack.ops.length > 0`, since a stateful/stateless call with no declared token surface has no way to be reconciled.

### Proof of Concept
Foundry fork test plan:
1. Deploy `Hinkal`, `EmporiumUpgradeable`, register it as external action id `N`.
2. Seed Emporium with a known ERC20/ETH balance (e.g., transfer 10 tokens directly to Emporium, or via `receive()` for ETH) to represent "off-books" funds already present in the contract (simulating dust/in-flight residue).
3. Attacker crafts `stack.ops = [{ endpoint: token, invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attacker, 10e18)) }]`, encodes it into `externalActionMetadata`.
4. Attacker builds `circomData` with `erc20TokenAddresses = []`, `amountChanges = []`, `slippageValues = []`, `onChainCreation = []`, and a locally generated valid proof for this zero-token-array case plus whatever no-op nullifier/root data is required to pass `performHinkalChecks`/`verifyProof`.
5. Call `Hinkal.transact(a, b, c, dimensions, circomData)`.
6. Assertions:
   - LHS: `sum(utxoSet[].amount)` returned/observable from `runAction` == `0`.
   - RHS: `token.balanceOf(attacker)` after minus before == `10e18` (nonzero).
   - Assert these two values are unequal, proving actual token flow (`10e18`) is not reflected anywhere in `utxoSet`, `onChainCommitments`, or the `balanceDif` check in `Hinkal.transact` (which never executed for this token because `erc20TokenAddresses.length == 0`).
   - Confirm `insertNullifiers`/`insertCommitments` recorded nothing for this asset, i.e., it left the pool with zero corresponding ledger entries.

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L162-184)
```text
    function handleOut(
        int256 balanceChange,
        CircomData calldata circomData,
        uint256 i
    ) internal returns (UTXO memory outUtxo) {
        // total change can be less than zero if there was some balance before the call -> that's why we have <=
        if (balanceChange <= 0) {
            return outUtxo;
        }

        transferERC20TokenOrETH(
            circomData.erc20TokenAddresses[i],
            msg.sender,
            uint256(balanceChange)
        );

        outUtxo = UTXO(
            uint256(balanceChange),
            circomData.erc20TokenAddresses[i],
            circomData.stealthAddressStructure,
            circomData.timeStamp
        );
    }
```

**File:** contracts/Hinkal.sol (L97-147)
```text
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

**File:** contracts/Hinkal.sol (L244-261)
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

        return
            IExternalActionV2(circomData.externalActionData.externalAddress)
                .runAction(circomData, deltaAmountChanges);
    }
```
