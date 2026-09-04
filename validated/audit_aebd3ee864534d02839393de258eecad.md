## Finding: Confirmed — Critical

### Title
Unsigned Emporium ops with `signerAddress == 0` + empty `erc20TokenAddresses` let any attacker execute arbitrary calls as the Emporium contract with zero balance accounting - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`, `contracts/CircomDataBuilder.sol`, `contracts/Hinkal.sol`)

### Summary
When `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `erc20TokenAddresses.length == 0`, `formInputForCircom` routes to `formInputEmporiumMin`, which only proves `message == Poseidon(messageSeed)` — a preimage the attacker trivially knows since they choose it themselves. `EmporiumUpgradeable.verifyWallet` skips all EIP-712 signature verification whenever `stack.signerAddress == address(0)`, so the attacker-crafted `EmporiumStack.ops` execute unauthenticated via `op.endpoint.call{value: op.value}(op.callData)` with `msg.sender == Emporium`, while both `Hinkal.transact`'s balance/slippage loop and `EmporiumUpgradeable.runAction`'s `balancesBefore/After` loop iterate zero times because `erc20TokenAddresses` is empty.

### Finding Description
The broken equality: **assets Emporium can move in a tx == assets accounted for in `balancesBefore`/`balancesAfter` (and in Hinkal's `oldBalances`/`newBalances`)**. The attacker breaks this by choosing `erc20TokenAddresses.length == 0` so no token is ever compared before/after the call in either accounting loop.

Path:
1. `CircomDataBuilder.formInputForCircom` (`contracts/CircomDataBuilder.sol:134-148`) selects `formInputEmporiumMin` when `externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0`.
2. `formInputEmporiumMin` (`contracts/CircomDataBuilder.sol:150-161`) only feeds `emporiumMessage`, `timeStamp`, `calldataHash` as public inputs — none of `amountChanges`, `erc20TokenAddresses`, `inputNullifiers`, or `outCommitments` are constrained, per the question's framing "proving only message == Poseidon(messageSeed)". Because the attacker is the direct caller of `Hinkal.transact` (not relaying a victim's signature), they fully control `circomData`, including `externalActionData.externalActionMetadata`, and can trivially satisfy this minimal proof.
3. `Hinkal.transact` (`contracts/Hinkal.sol:76-147`) computes `oldBalances`/`newBalances` and the balance-diff/slippage `require` loop only over `circomData.erc20TokenAddresses` — with length 0 this entire accounting block never executes.
4. `_externalTransact` (`contracts/Hinkal.sol:234-261`) calls `EmporiumUpgradeable.runAction` with `deltaAmountChanges` of length 0.
5. `EmporiumUpgradeable.runAction` (`contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol:76-160`) decodes the attacker-controlled `EmporiumStack` and calls `verifyWallet`. In `verifyWallet` (lines 302-349), if `stack.signerAddress == address(0)` the function returns immediately after marking the message used — **no EIP-712 signature check occurs at all**.
6. Because `stack.signerAddress == address(0)`, the `op.invokeWallet && stack.signerAddress != address(0)` condition (line 98) is false for every op, so every op falls into "CASE 2: Stateless Interaction" (lines 102-113): `op.endpoint.call{value: op.value}(op.callData)` executed with `msg.sender == Emporium`. The only restriction is that the call selector isn't `callHinkalWallet`/`doSendToRelay`.
7. `runAction`'s own `balancesBefore`/`balancesAfter` accounting (lines 85-151) also iterates `circomData.erc20TokenAddresses`, which is empty, so any token the ops actually touch is entirely unaccounted for.

Attacker's exact call: `Hinkal.transact` with `circomData.externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `circomData.erc20TokenAddresses = []`, and `externalActionMetadata` decoding to `EmporiumStack{ signerAddress: address(0), ops: [{ endpoint: <victimToken>, invokeWallet: false, value: 0, callData: abi.encodeWithSelector(IERC20.transfer.selector, attacker, balance) }] }` (or `approve(attacker, type(uint256).max)` for a delayed drain via `transferFrom`), plus a trivially-generated Min-circuit proof for their own chosen `emporiumMessage`.

Existing guards fail because: `onlyAllowedRecipient` only checks `msg.sender == Emporium contract`, not who initiated the call; `verifyWallet`'s signature check is entirely bypassed by `signerAddress == 0`; `performHinkalChecks`'s `calldataHash` integrity check only verifies the attacker's own crafted `circomData` is self-consistent, it does not bind the ops to any authorized party; and the balance-diff/slippage invariant in both `Hinkal.transact` and `EmporiumUpgradeable.runAction` is vacuously satisfied because it loops zero times over an empty token array.

### Impact Explanation
Any unprivileged attacker can force the Emporium contract to execute an arbitrary external call as itself, unaccounted for by any balance check, allowing them to `transfer`/`approve`-drain any ERC20 (or ETH via `value`) balance the Emporium contract holds — including funds momentarily resident in Emporium as part of other users' in-flight multi-op transactions or protocol fee balances. This is direct theft of shielded/in-flight user funds and unauthorized execution of calls a wallet owner or prover never authorized, matching Critical severity. The attack is repeatable for every distinct `emporiumMessage` (only constrained to be unused once).

### Likelihood Explanation
Preconditions are minimal: attacker needs only to call `Hinkal.transact` themselves (as `originalSender`/no relay, or via a relay of their choosing), generate the trivial Min-circuit proof for a self-chosen `emporiumMessage`, and craft `externalActionMetadata`. No special tree state, no victim cooperation, and no privileged role is required. The only prerequisite for value extraction is that Emporium holds a nonzero balance of the targeted token at call time, which is expected during normal operation (e.g., intermediate legs of swaps/settlements route funds through Emporium).

### Recommendation
- Do not allow the `formInputEmporiumMin`/empty-`erc20TokenAddresses` path to be combined with execution of arbitrary, unsigned ops. Either require `stack.signerAddress != address(0)` (mandatory signature) whenever the Min-circuit path is used, or forbid the Min-circuit selection entirely for `EmporiumUpgradeable.runAction` and always require `erc20TokenAddresses` to enumerate every token/ETH balance touched by the ops so the before/after accounting is non-vacuous.
- Bind the ops (`_hashEmporiumOps`) into the circuit-verified `calldataHash`/message in a way that is enforced even for the "no signer" branch, or eliminate the "no signer, no signature" branch altogether.
- Add strict allow-listing of callable `op.endpoint`/selectors when `signerAddress == address(0)`, at minimum disallowing `approve`, `transfer`, `transferFrom` on registered vault-held tokens.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable` (registered as allowed recipient and as `externalActionMap[HINKAL_EMPORIUM_ACTION_ID]`), and a mock verifier that returns `true` for the Min verifier ID (or use the real Min circuit with locally generated proof for attacker-chosen `messageSeed`).
2. Fund `EmporiumUpgradeable` with `100e18` of `MockERC20` (simulating in-flight/protocol funds).
3. From an attacker EOA with no prior deposits, call `Hinkal.transact` with `dimensions` matching the Min verifier ID, `circomData.erc20TokenAddresses = []`, `circomData.externalActionData = { externalActionId: HINKAL_EMPORIUM_ACTION_ID, externalAddress: address(emporium) }`, and `externalActionMetadata` ABI-encoding `EmporiumStack{ signerAddress: address(0), ops: [{ endpoint: address(mockToken), invokeWallet: false, value: 0, callData: abi.encodeWithSelector(IERC20.transfer.selector, attacker, 100e18) }] }`.
4. Assert equality violated: `mockToken.balanceOf(emporium)` before == `100e18`, after == `0`; `mockToken.balanceOf(attacker)` after == `100e18`; while `Hinkal.transact` and `EmporiumUpgradeable.runAction`'s balance loops recorded zero entries (`circomData.erc20TokenAddresses.length == 0`), i.e., no `require` in either loop ever fired to catch the movement.
5. Confirm `verifyWallet` executed the no-signature branch (`signerAddress == address(0)`) and no revert occurred despite no valid EIP-712 signature being supplied. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-160)
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-349)
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

        bytes32 hashedMessage = _hashTypedDataV4(
            keccak256(
                abi.encode(
                    EMPORIUM_SIGNATURE_TYPEHASH,
                    circomData.emporiumMessage,
                    _hashEmporiumOps(stack.ops),
                    stack.maxFee,
                    stack.deadline
                )
            )
        );

        (address recoveredAddress, ECDSA.RecoverError err) = ECDSA.tryRecover(
            hashedMessage,
            stack.v,
            stack.r,
            stack.s
        );
        bool verified = err == ECDSA.RecoverError.NoError &&
            recoveredAddress == stack.signerAddress;
        if (!verified) {
            revert InvalidSignature();
        }

        if (block.timestamp > stack.deadline) {
            revert SignatureExpired();
        }

        if (circomData.feeStructure.flatFee > stack.maxFee) {
            revert FeeExceedsSignedMax();
        }
    }
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
