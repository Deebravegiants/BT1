### Title
Emporium "Min-proof" path bypasses all balance accounting and wallet-signature checks, letting any unprivileged caller drain Emporium's held ETH/tokens via arbitrary calls - (File: contracts/CircomDataBuilder.sol, contracts/Hinkal.sol, contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
When `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `erc20TokenAddresses.length == 0`, `formInputForCircom` routes to `formInputEmporiumMin`, which only constrains `emporiumMessage`, `timeStamp`, and `calldataHash` — no UTXO/nullifier/balance semantics are proven at all. Because every balance-accounting loop on both the `Hinkal.transact` side and the `EmporiumUpgradeable.runAction` side is bounded by `circomData.erc20TokenAddresses.length`, choosing an empty token array makes all of them silently no-op, and setting `EmporiumStack.signerAddress == address(0)` additionally skips the EIP-712 signature check in `verifyWallet`. The combination lets any address run arbitrary `EmporiumOperation`s from Emporium's own identity/balance with zero checks.

### Finding Description
Broken equality: "assets Emporium can move in a tx" should equal "assets accounted in balancesBefore/balancesAfter", but with an empty `erc20TokenAddresses` array both sides collapse to the empty set while Emporium's arbitrary calls (and its ETH/token balance) are unconstrained.

Trace:
1. `formInputForCircom` selects the minimal-proof branch purely from `externalActionId` and `erc20TokenAddresses.length == 0`: [1](#0-0) 
This circuit only proves `message == Poseidon(messageSeed)` — an attacker trivially satisfies this with a self-chosen seed; it proves nothing about UTXO ownership, nullifiers, or balances.

2. In `Hinkal.transact`, the only per-token accounting/slippage/balance-diff loop is bounded by `circomData.erc20TokenAddresses.length`: [2](#0-1) 
With length 0, this loop (including the `msg.value` ETH-leg branch at lines 100-104) never executes, so no `slippage param is violated` or `Balance Diff` checks apply, and `insertNullifiers`/`insertCommitments` process empty arrays.

3. `_externalTransact` deposits into the action contract only for indices in `erc20TokenAddresses` (empty ⇒ none), then unconditionally calls `runAction`: [3](#0-2) 

4. `EmporiumUpgradeable.runAction` is gated only by `onlyAllowedRecipient` (i.e., caller is Hinkal core) — it performs no check that `erc20TokenAddresses` is non-empty or matches the ops performed: [4](#0-3) 
Its own `balancesBefore`/`balancesAfter`/`BalanceChangeShouldBePositive` accounting loop (lines 132-151) is likewise bounded by the same empty `circomData.erc20TokenAddresses`, so it is a complete no-op: [5](#0-4) 

5. `verifyWallet` skips signature verification entirely when `stack.signerAddress == address(0)`, only marking the message as used: [6](#0-5) 

6. With `signerAddress == 0`, every op falls into the "stateless" branch, which lets Emporium execute an arbitrary low-level call with attacker-chosen `endpoint`, `callData`, and `value` (drawn from Emporium's own ETH balance), the only restriction being the selector isn't `callHinkalWallet`/`doSendToRelay`: [7](#0-6) 

Root cause: the "Min proof" optimization for Emporium assumes `erc20TokenAddresses.length == 0` implies "no assets are at stake," but nothing prevents `EmporiumStack.ops` from moving assets that Emporium already holds (ETH dust, leftover ERC20 balances from prior ops/transactions, tokens sent to Emporium by mistake or via a partially-completed multi-op flow) or from making arbitrary calls to other allow-listed contracts. Since no balance loop runs on either side, no accounting requires that assets moved by `ops` correspond to any `amountChanges`/UTXOs, and no signature is required because `signerAddress == 0`.

### Impact Explanation
Any unprivileged attacker who can observe (or cause) Emporium to hold a nonzero ETH or ERC20 balance can submit a `transact` call using the Emporium Min-proof path with a self-authored `EmporiumStack` (`signerAddress = 0`, arbitrary `ops`) that directs Emporium to call `token.transfer(attacker, balance)` or send its ETH balance to the attacker, with zero on-chain accounting, zero nullifier consumption, and zero real proof-of-ownership. This is direct theft of funds held by (or in flight through) the Emporium contract — Critical severity, matching "direct theft of shielded or in-flight user funds" / "executing calls or moving assets a wallet owner or prover never authorised."

### Likelihood Explanation
Preconditions: Emporium must hold a nonzero balance at the moment of attack (dust/rounding remainders, leftover balances from prior incomplete op sequences, or ETH/tokens sent to Emporium by other flows). No privileged role, no relayer collusion, and no valid EIP-712 signature are required because `signerAddress == 0` bypasses `verifyWallet`'s signature check. Attacker cost is a single transaction with a self-generated Min proof (trivial, since it only proves knowledge of a self-chosen seed) and a hand-crafted `EmporiumStack`. The attack is repeatable every time Emporium accumulates a nonzero balance.

### Recommendation
- Require `erc20TokenAddresses.length > 0` (or otherwise enumerate every token touched by `ops`) whenever `externalActionData.externalActionId == HINKAL_EMPORIUM_ACTION_ID`, so the balance-accounting loops in both `Hinkal.transact` and `EmporiumUpgradeable.runAction` cannot be trivially bypassed by choosing an empty array.
- Do not allow `formInputEmporiumMin` to skip balance/slippage checks; if a "minimal circuit" optimization is desired, it must still force `EmporiumUpgradeable.runAction` to snapshot and reconcile balances for every token actually touched by `ops`/`op.endpoint` calls (e.g., derive the token set from decoded op calldata, or require the caller to declare it and revert if it's empty while `ops.length > 0`).
- Do not allow `EmporiumStack.signerAddress == address(0)` to fully bypass signature verification unless there is an independent guarantee (e.g., the empty-token-array balance-check bypass above is closed) that no asset movement can occur without accounting.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `EmporiumUpgradeable` (as a registered external action with `HINKAL_EMPORIUM_ACTION_ID`), and a test ERC20/mint some tokens or send ETH directly to the Emporium proxy address to simulate "Emporium already holds funds" (e.g., via `vm.deal(emporiumAddress, 10 ether)` or `token.transfer(emporiumAddress, 1000e18)`).
2. As an attacker EOA with no prior deposits/UTXOs, construct `CircomData` with:
   - `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`
   - `erc20TokenAddresses = []`
   - `externalActionData.externalActionMetadata` = ABI-encoded `EmporiumStack{signerAddress: address(0), ops: [{endpoint: token, invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attacker, 1000e18))}]}`
   - `emporiumMessage = Poseidon(attackerChosenSeed)` matching a locally generated Min-circuit proof (`a,b,c`).
3. Call `Hinkal.transact(a,b,c,dimensions,circomData)` from the attacker.
4. Assert:
   - Proof verifies and tx succeeds.
   - `token.balanceOf(attacker)` increases by 1000e18 while `token.balanceOf(emporium)` decreases by the same, with `oldBalances == newBalances` (both empty arrays, i.e., Hinkal.sol's own accounting never observed the movement) — demonstrating the equality "assets moved == assets accounted" is violated.
   - No nullifiers were inserted (`insertNullifiers` called with empty arrays) and no UTXOs were consumed/created for this theft.

### Citations

**File:** contracts/CircomDataBuilder.sol (L134-161)
```text
    function formInputForCircom(
        uint256 chainId,
        address verifyingContract,
        CircomData calldata circomData
    ) internal pure returns (uint256[] memory) {
        if (
            circomData.externalActionData.externalActionId ==
            HINKAL_EMPORIUM_ACTION_ID &&
            circomData.erc20TokenAddresses.length == 0
        ) {
            return formInputEmporiumMin(circomData);
        } else {
            return formInputNormal(chainId, verifyingContract, circomData);
        }
    }

    function formInputEmporiumMin(
        CircomData calldata circomData
    ) internal pure returns (uint256[] memory input) {
        input = new uint256[](circomData.publicSignalCount);

        uint16 index = 0;

        input[index++] = circomData.emporiumMessage;

        input[index++] = circomData.timeStamp;
        input[index++] = circomData.calldataHash;
    }
```

**File:** contracts/Hinkal.sol (L88-147)
```text
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

**File:** contracts/Hinkal.sol (L234-261)
```text
    function _externalTransact(
        CircomData calldata circomData
    ) internal returns (UTXO[] memory) {
        require(
            externalActionMap[circomData.externalActionData.externalActionId] ==
                circomData.externalActionData.externalAddress &&
                circomData.externalActionData.externalAddress != address(0),
            "Unknown externalAddress"
        );

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-90)
```text
    function runAction(
        CircomData calldata circomData,
        int256[] calldata deltaAmountChanges
    ) external override onlyAllowedRecipient returns (UTXO[] memory) {
        EmporiumStack memory stack = abi.decode(
            circomData.externalActionData.externalActionMetadata,
            (EmporiumStack)
        );

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-160)
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

        if (utxoSetLength < circomData.erc20TokenAddresses.length) {
            utxoSet.skipLast(
                circomData.erc20TokenAddresses.length - utxoSetLength
            );
        }

        return utxoSet;
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
