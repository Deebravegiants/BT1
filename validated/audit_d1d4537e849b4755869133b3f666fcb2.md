Confirmed via code tracing.

### Title
Emporium ETH drain via `HINKAL_EMPORIUM_ACTION_ID` + empty `erc20TokenAddresses` bypasses all balance accounting - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
When `circomData.externalActionData.externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `circomData.erc20TokenAddresses.length == 0`, `CircomDataBuilder.formInputForCircom` routes to `formInputEmporiumMin`, which only feeds `MainEVMCircuitMin` (3 public signals: `emporiumMessage`, `outTimeStamp`, `calldataHash`). This circuit never constrains ownership, nullifiers, or root hash, and every balance-accounting loop in both `Hinkal.transact` and `EmporiumUpgradeable.runAction` is indexed by the same empty `erc20TokenAddresses` array, so ETH moved by `EmporiumUpgradeable.runAction`'s arbitrary `op.endpoint.call{value: op.value}` is never checked against anything.

### Finding Description
Broken equality: `set of assets moved by op.endpoint.call{value: op.value}` (ETH, attacker-controlled `dustAmount`) `!= Σ balancesAfter[i]-balancesBefore[i] for i in erc20TokenAddresses` (0 terms, since `erc20TokenAddresses.length == 0`).

Trace:
- `CircomDataBuilder.formInputForCircom` special-cases `HINKAL_EMPORIUM_ACTION_ID` with `erc20TokenAddresses.length == 0` and calls `formInputEmporiumMin`, producing only `[emporiumMessage, timeStamp, calldataHash]` [1](#0-0) .
- The corresponding circuit `MainEVMCircuitMin` only constrains `message === Poseidon(messageSeed)`; it has no `spendingPublicKey`, `nullifyingPrivateKey`, `rootHashHinkal`, or `SignatureVerifier` component at all [2](#0-1) . `SignatureVerifier` (used by the full `MainEVMCircuit`) is simply not part of this path.
- `HinkalHelper.dimensionsCheck` only requires internal array lengths to match `dimensions.tokenNumber`, which the attacker sets to 0 consistently — it does not forbid `tokenNumber == 0` for the Emporium action [3](#0-2) .
- In `Hinkal.transact`, `oldBalances`/`newBalances` and the balance-diff/slippage/UTXO-accounting loop are all built over `circomData.erc20TokenAddresses`, which is empty, so the loop body never executes — no ETH or token movement is checked at the Hinkal level [4](#0-3) .
- `Hinkal._externalTransact` builds `deltaAmountChanges` with `length == erc20TokenAddresses.length == 0` and forwards it to `runAction` [5](#0-4) .
- `EmporiumUpgradeable.runAction` computes `balancesBefore`/`balancesAfter` over the same empty `erc20TokenAddresses`, so those arrays are empty and the reconciliation loop at the end never runs [6](#0-5) . Meanwhile the `stack.ops` loop unconditionally executes `op.endpoint.call{value: op.value}(op.callData)` for the stateless case (`stack.signerAddress == address(0)`), and `verifyWallet` for `signerAddress == address(0)` only marks `usedMessages` and returns — no signature check at all [7](#0-6) .
- `EmporiumUpgradeable` has a public `receive() external payable {}`, so ETH can accumulate on the contract (dust, rounding, prior partial operations) [8](#0-7) .

Exploit: attacker deposits/observes any ETH sitting on `EmporiumUpgradeable` (e.g. via its `receive()`), encodes `EmporiumStack{signerAddress: address(0), ops: [{endpoint: attackerEOA, value: dustAmount, callData: ""}]}` as `externalActionMetadata`, sets `erc20TokenAddresses = []`, `externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `dimensions.tokenNumber = 0`, generates a Groth16 proof for `MainEVMCircuitMin` (only needs `message == Poseidon(messageSeed)`), and calls `Hinkal.transact`. `performHinkalChecks` → `verifyProof` (registered verifier for this `tokenNumber=0`/`HINKAL_EMPORIUM_ACTION_ID` combo, e.g. `mainEVMCircuitMin0v4`) → `rootHashExists` (attacker just reuses any valid known root, since `rootHashHinkal` is not a constrained circuit signal here) all pass, then `EmporiumUpgradeable.runAction` sends `dustAmount` ETH to the attacker with zero balance reconciliation.

### Impact Explanation
Direct theft of ETH held by `EmporiumUpgradeable` that belongs to the protocol or other users (any residual balance sitting on the contract), with no proof of ownership, no nullifier, and no balance equation enforcing it. This matches the Critical category ("direct theft of shielded or in-flight user funds ... proof or nullifier verification bypass") since the "proof" supplied constrains nothing relevant to the funds moved. It is repeatable for as long as ETH balance accumulates on the Emporium contract, and each `emporiumMessage` can only be used once (`usedMessages`) but a fresh message can be generated for each drain attempt at negligible cost (just a Poseidon preimage and a proof).

### Likelihood Explanation
Preconditions: `EmporiumUpgradeable` must hold ETH (achievable via its own `receive()`, dust from prior legitimate ops, or rounding remainders) and the `HINKAL_EMPORIUM_ACTION_ID`/`tokenNumber=0` verifier must be registered (which appears to be the intended supported configuration given `formInputEmporiumMin` and the `mainEVMCircuitMin0v4` verifier exist specifically for this case). Attacker cost is minimal (one proof generation, one `transact` call, no privileged role needed). Fully feasible for any unprivileged EOA.

### Recommendation
When routing through the Emporium-min path (`erc20TokenAddresses.length == 0`), either (a) forbid any ETH-valued, non-wallet-invoking `op.value` in `EmporiumUpgradeable.runAction` when `stack.signerAddress == address(0)` and `erc20TokenAddresses` is empty, or (b) always account for ETH (`address(0)`) balance changes in `runAction`'s before/after tracking regardless of `erc20TokenAddresses` contents, requiring any net ETH outflow to be justified by `deltaAmountChanges`/UTXO accounting. More robustly, require that `erc20TokenAddresses` includes `address(0)` whenever any `op.value > 0` is present in the decoded `EmporiumStack`, and reject the minimal-circuit path unless all `op.value == 0`.

### Proof of Concept
Foundry fork test:
1. Deploy/fork Hinkal + EmporiumUpgradeable stack with the `HINKAL_EMPORIUM_ACTION_ID`/`tokenNumber=0` verifier registered (`mainEVMCircuitMin0v4`).
2. `vm.deal(address(emporium), dustAmount)` to simulate leftover ETH on Emporium.
3. Off-chain (snarkjs), generate a valid Groth16 proof for `MainEVMCircuitMin` with an arbitrary `messageSeed`, setting `message = Poseidon(messageSeed)` as `circomData.emporiumMessage`.
4. Build `circomData` with `erc20TokenAddresses = []`, `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `externalActionMetadata = abi.encode(EmporiumStack({signerAddress: address(0), ops: [EmporiumOperation({endpoint: attacker, invokeWallet: false, value: dustAmount, callData: ""})], ...}))`, `dimensions.tokenNumber = 0`, valid `rootHashHinkal`/`rootHashHinkalIndex` from an existing root.
5. Call `hinkal.transact(a, b, c, dimensions, circomData)` from attacker EOA.
6. Assert `attacker.balance` increased by `dustAmount` and `address(emporium).balance` decreased by `dustAmount`, while `circomData.erc20TokenAddresses.length == 0` throughout, proving no equation in `Hinkal.transact` or `EmporiumUpgradeable.runAction` ever constrained this ETH movement.

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

**File:** circuits/MainEVMCircuitMin.circom (L1-18)
```text

pragma circom 2.1.6;

include "../../node_modules/circomlib/circuits/poseidon.circom";

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

**File:** contracts/HinkalHelper.sol (L64-90)
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
```

**File:** contracts/Hinkal.sol (L76-147)
```text
            UTXO[] memory utxoSet;

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-160)
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L369-370)
```text
    receive() external payable {}
}
```
