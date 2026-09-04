### Title
Unsigned Emporium ops with empty `erc20TokenAddresses` drain arbitrary ETH held by Emporium via unaccounted `op.value` transfer - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
When `CircomData.erc20TokenAddresses` is empty and `externalActionId == HINKAL_EMPORIUM_ACTION_ID`, `CircomDataBuilder.formInputForCircom` routes to `formInputEmporiumMin`, which only feeds `MainEVMCircuitMin` a self-computed `message <== Poseidon(1)([messageSeed])` with no constraint tying it to any UTXO, nullifier, or signature. Combined with `EmporiumUpgradeable.verifyWallet` short-circuiting all signature checks when `stack.signerAddress == address(0)`, and `Hinkal.transact`'s balance-accounting loop being skipped entirely for a zero-length `erc20TokenAddresses` array, an attacker can force `runAction` to execute an arbitrary `op.endpoint.call{value: op.value}(...)` that drains the Emporium contract's full ETH balance with no accounting check anywhere in the call path.

### Finding Description
Broken equality: assets moved by `op.endpoint.call{value: op.value}("")` in `EmporiumUpgradeable.runAction` (line 112) should equal the `balanceDif` computed and validated in `Hinkal.transact`'s per-token loop (lines 97-147). With `circomData.erc20TokenAddresses.length == 0`, that loop body never executes — `balanceDif` is never computed, and the `require(balanceDif == ...)` check that is supposed to tie every asset movement to consumed/created UTXOs is never reached.

Path traced:
1. `HinkalHelper.dimensionsCheck` and `checkOnchainCreation` only validate array lengths against `Dimensions{0,0,0}`; with all arrays empty they trivially pass. [1](#0-0) 
2. `CircomDataBuilder.formInputForCircom` detects `externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0` and calls `formInputEmporiumMin`, producing only `[emporiumMessage, timeStamp, calldataHash]` as public input — `rootHashHinkal` is not even part of this input. [2](#0-1) 
3. `MainEVMCircuitMin` constrains nothing except `message <== Poseidon(1)([messageSeed])`; the attacker picks any `messageSeed` off-chain, computes `message`, sets `circomData.emporiumMessage = message`, and generates a trivially-satisfiable proof requiring no UTXO ownership, no nullifier, no signature. [3](#0-2) 
4. `Hinkal.transact` verifies this proof against `VerifierEVMMin0v4` (registered at `buildVerifierId({0,0,0}, HINKAL_EMPORIUM_ACTION_ID)`), and only requires `rootHashExists` for *some* valid root (irrelevant to this circuit's inputs), then calls `_externalTransact`. [4](#0-3) 
5. `_externalTransact`'s `deltaAmountChanges` loop is over `erc20TokenAddresses.length == 0` (no-op), then calls `EmporiumUpgradeable.runAction(circomData, [])`. [5](#0-4) 
6. Inside `runAction`, `verifyWallet` marks the message as used and **returns immediately without any signature check** because `stack.signerAddress == address(0)`. [6](#0-5) 
7. The `ops` loop executes `op.endpoint.call{value: op.value}(op.callData)` for the attacker's chosen `endpoint`/`value`/`callData`, e.g. `value = address(emporium).balance`, draining all Emporium ETH to the attacker's contract. [7](#0-6) 
8. `runAction`'s own balance-accounting loop (`balancesBefore`/`balancesAfter`) is also over `circomData.erc20TokenAddresses.length == 0`, so it produces no check on the ETH movement either. [8](#0-7) 
9. Back in `Hinkal.transact`, the same zero-length loop skips `balanceDif` computation entirely, so no `require` fires, and `insertNullifiers`/`insertCommitments` are called on empty arrays (no-ops). [9](#0-8) 

Root cause: the "Min" circuit/input path designed for stateless/self-authorized Emporium actions provides zero binding between the proof and any value transfer, and it is reachable with `erc20TokenAddresses = []`, which simultaneously disables every balance-accounting guard in both `Hinkal.transact` and `EmporiumUpgradeable.runAction`. The `signerAddress == address(0)` branch in `verifyWallet`, intended presumably for a different trust model, removes the last remaining authorization check (EIP-712 signature).

### Impact Explanation
Any unprivileged attacker can drain the full ETH balance held by the `EmporiumUpgradeable` proxy — funds belonging to any user with ETH parked there (e.g., in-flight funds from a multi-step signed session, or plain `receive()` deposits, since `EmporiumUpgradeable` has an unrestricted `receive() external payable {}`). No nullifier is consumed, no signature is checked, no UTXO is destroyed — a direct, repeatable theft of protocol/user in-flight ETH with zero cost beyond gas and proof generation. This meets the Critical bar ("direct theft of shielded or in-flight user funds ... proof or nullifier verification bypass").

### Likelihood Explanation
Preconditions are all attacker-controllable and require no privilege: Emporium must already be registered (a normal deployment precondition, not privileged access by the attacker) and must hold ETH (via any prior deposit/op or a plain `send()`, which is unrestricted). The attacker needs only to craft `CircomData`/`Dimensions` fields, generate a snarkjs proof for the trivial `MainEVMCircuitMin` relation, and submit `transact`. This is fully repeatable each time Emporium accumulates ETH balance.

### Recommendation
- Do not allow `erc20TokenAddresses.length == 0` (or any zero-length token array) to bypass the `balanceDif` accounting loop in `Hinkal.transact` when an external action can move value; require at least an ETH sentinel entry whenever `op.value > 0` is possible.
- Remove or gate the `stack.signerAddress == address(0)` short-circuit in `EmporiumUpgradeable.verifyWallet` so it can never skip authorization when `ops` contain non-zero `value` or arbitrary `callData`/`endpoint` — require an explicit, circuit-bound or signature-bound authorization for every stateless op.
- Bind the `MainEVMCircuitMin`/`formInputEmporiumMin` path to a real, spendable commitment or a signed authorization instead of an attacker-chosen `messageSeed`, so proof generation cannot be done without owning value or a valid signature.

### Proof of Concept
Foundry fork test:
1. Deploy/fork with `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable` registered at `HINKAL_EMPORIUM_ACTION_ID`, and `VerifierEVMMin0v4` registered at `buildVerifierId(Dimensions(0,0,0), HINKAL_EMPORIUM_ACTION_ID)`.
2. Seed Emporium with ETH via `vm.deal(address(emporium), 10 ether)` or a legitimate prior op.
3. Off-chain (snarkjs), pick `messageSeed`, compute `message = Poseidon(1)([messageSeed])`, generate a valid Groth16 proof for `MainEVMCircuitMin` with public inputs `[message, outTimeStamp, calldataHash]`.
4. Build `CircomData` with `erc20TokenAddresses = []`, `amountChanges = []`, etc. all empty, `emporiumMessage = message`, `externalActionData = {externalAddress: address(emporium), externalActionId: HINKAL_EMPORIUM_ACTION_ID, externalActionMetadata: abi.encode(EmporiumStack{signerAddress: address(0), ops: [{endpoint: attackerContract, invokeWallet: false, value: 10 ether, callData: ""}], maxFee: 0, deadline: type(uint256).max})}`, `calldataHash = getHashedCalldata(circomData)`.
5. Call `hinkal.transact(a, b, c, Dimensions(0,0,0), circomData)`.
6. Assert: `attackerContract.balance` increased by `10 ether`, `emporium.balance == 0`, no entry was added to `nullifiers` mapping, and the transaction did not revert on any `balanceDif`/slippage `require`.

### Citations

**File:** contracts/HinkalHelper.sol (L64-124)
```text
    function dimensionsCheck(
        CircomData calldata circomData,
        Dimensions calldata dimensions
    ) internal pure {
        require(
            circomData.erc20TokenAddresses.length == dimensions.tokenNumber,
            "erc20TokenAddresses number should be equal to token number"
        );
        require(
            circomData.amountChanges.length == dimensions.tokenNumber,
            "AmountChanges number should be equal to token number"
        );

        require(
            circomData.onChainCreation.length == dimensions.tokenNumber,
            "onchain creation is equal to tokens count"
        );

        require(
            circomData.slippageValues.length == dimensions.tokenNumber,
            "slippageValues length should be equal to tokens count"
        );

        require(
            circomData.inputNullifiers.length == dimensions.tokenNumber,
            "InputNullifiers number should be equal to token number"
        );

        uint previousNullifierAmount = circomData.inputNullifiers.length > 0
            ? circomData.inputNullifiers[0].length
            : 0;
        for (uint i = 1; i < circomData.inputNullifiers.length; i++) {
            require(
                circomData.inputNullifiers[i].length == previousNullifierAmount,
                "Nullifier amount should be equal"
            );
        }
        require(
            previousNullifierAmount == dimensions.nullifierAmount,
            "Actual and Claimed Nullifier Amount should be equal"
        );

        require(
            circomData.outCommitments.length == dimensions.tokenNumber,
            "OutCommitments number should be equal to token number"
        );

        uint previousCommitmentAmount = circomData.outCommitments.length > 0
            ? circomData.outCommitments[0].length
            : 0;

        for (uint i = 1; i < circomData.outCommitments.length; i++) {
            require(
                circomData.outCommitments[i].length == previousCommitmentAmount,
                "Commitment amount should be equal"
            );
        }
        require(
            previousCommitmentAmount == dimensions.outputAmount,
            "Actual and Claimed Commitment Amount should be equal"
        );
```

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

**File:** circuits/MainEVMCircuitMin.circom (L6-18)
```text
template MainEVMCircuitMin() {
  // Public inputs:
  signal input outTimeStamp;
  signal input calldataHash;

  // Private inputs:
  signal input messageSeed;

  // outputs:
  signal output message;

  message <== Poseidon(1)([messageSeed]);
}
```

**File:** contracts/Hinkal.sol (L36-66)
```text
    ) public payable nonReentrant {
        {
            uint256[] memory inputForCircom = hinkalHelper.performHinkalChecks(
                circomData,
                dimensions,
                msg.sender
            );

            require(
                verifyProof(
                    a,
                    b,
                    c,
                    inputForCircom,
                    buildVerifierId(
                        dimensions,
                        circomData.externalActionData.externalActionId
                    )
                ),
                "Invalid Proof"
            );
            // Root Hash Validation
            require(
                rootHashExists(
                    circomData.rootHashHinkal,
                    circomData.rootHashHinkalIndex
                ),
                "Hinkal Root Hash is Incorrect"
            );
        }
        hinkalHelper.performSideEffects(circomData);
```

**File:** contracts/Hinkal.sol (L88-167)
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

            if (circomData.hookData.postHookContract != address(0)) {
                ITransactHook transactHook = ITransactHook(
                    circomData.hookData.postHookContract
                );
                transactHook.afterTransact(circomData);
            }

            insertNullifiers(
                circomData.inputNullifiers,
                circomData.onChainCreation
            );

            insertCommitments(
                circomData.outCommitments,
                circomData.encryptedOutputs,
                onChainCommitments,
                circomData.onChainCreation
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-151)
```text
        uint256[] memory balancesBefore = getBalancesForArray(
            circomData.erc20TokenAddresses
        );

        verifyWallet(stack, circomData);

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

        payRelayFees(circomData, stack.signerAddress, deltaAmountChanges);

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
