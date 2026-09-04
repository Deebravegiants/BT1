### Title
Emporium `EMPORIUM_SIGNATURE_TYPEHASH` doesn't bind `stealthAddressStructure`/`rootHashHinkal`, letting any unrelated prover hijack a harvested signed `EmporiumStack` and steal the residual Emporium balance - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.verifyWallet` authenticates only `emporiumMessage`, the hash of `stack.ops`, `maxFee`, and `deadline` via `EMPORIUM_SIGNATURE_TYPEHASH` [1](#0-0) . It never binds `circomData.rootHashHinkal`, `erc20TokenAddresses`, `amountChanges`, or `stealthAddressStructure` to the signer's authorization. Since `handleOut` mints the leftover Emporium balance as a UTXO to whichever `circomData.stealthAddressStructure` the *current* transaction's prover supplies [2](#0-1) , any unrelated party who obtains the signed `(v,r,s,signerAddress,ops,maxFee,deadline,emporiumMessage)` tuple can wrap it in a brand-new `CircomData` (with their own valid proof/rootHash and their own destination) and redirect the residual value to themselves.

### Finding Description
The broken equality: *(destination of the residual UTXO created from the signer's wallet assets moved by the signed `ops`) should equal (a destination the wallet owner actually authorized)*. In practice it equals *(whatever `circomData.stealthAddressStructure` the caller who supplies the ZK proof for `runAction` chooses)*, which is unconstrained by the signature.

Trace:
- `verifyWallet` recomputes `hashedMessage = _hashTypedDataV4(keccak256(abi.encode(EMPORIUM_SIGNATURE_TYPEHASH, circomData.emporiumMessage, _hashEmporiumOps(stack.ops), stack.maxFee, stack.deadline)))` and checks `ecrecover == stack.signerAddress` [3](#0-2) . The only anti-replay state is `$.usedMessages[circomData.emporiumMessage]` [4](#0-3) .
- `runAction` executes `stack.ops` against `stack.signerAddress`'s `IHinkalWallet`, moving the signer's real assets, then computes `balanceChange` and calls `handleOut(balanceChange, circomData, i)` [5](#0-4) .
- `handleOut` builds the output `UTXO` using `circomData.stealthAddressStructure` taken directly from the calldata of the *current* call, with no cross-check against `stack.signerAddress` or anything the signer signed [2](#0-1) .
- `formBasicInput` does place `stealthAddressStructure.H1x/H1y/stealthAddress` into the SNARK public input vector [6](#0-5) , but this is the *prover's own* freely chosen witness value for their own proof — it is not tied to the EIP-712 signature at all, so a completely independent attacker can supply their own valid proof (over their own `rootHashHinkal`/nullifiers) alongside the harvested stack.
- `HinkalHelper.performHinkalChecks`/`dimensionsCheck`/`checkOnchainCreation` only check internal self-consistency of `circomData` (`getHashedCalldata == calldataHash`, dimension lengths, `originalSender == msg.sender` when no relay) [7](#0-6)  — none of these tie `stealthAddressStructure` or `rootHashHinkal` back to `stack.signerAddress`.
- `Hinkal.transact` verifies the proof and root hash, then calls `_externalTransact` → `EmporiumUpgradeable.runAction` [8](#0-7) ; the slippage/balance checks only ensure the *attacker's own* declared `slippageValues`/`amountChanges` reconcile with the observed balance delta, which the attacker fully controls [9](#0-8) .

Attack: victim signs an `EmporiumStack` (ops moving wallet funds into Emporium, `emporiumMessage`=M). This signature — plus `ops`, `maxFee`, `deadline`, `signerAddress` — is visible in plaintext once broadcast (mempool, relay API, previous tx). Attacker copies the tuple, builds their own `CircomData` (own `rootHashHinkal`/nullifiers, own `erc20TokenAddresses`/`amountChanges`/`slippageValues` matching the expected residual, own `stealthAddressStructure` = attacker's), generates a valid proof for their own UTXOs, and submits `transact(...)` before the victim's legitimate relay does. `verifyWallet` still passes (all EIP-712-signed fields are identical), `usedMessages[M]` gets set (blocking the legitimate submission), the signer's assets move via `ops`, and the residual balance is minted as a UTXO under the attacker's `stealthAddressStructure`.

### Impact Explanation
Direct theft of value that left the wallet owner's assets via their own valid EIP-712 signature but is redirected into a shielded UTXO controlled by an unrelated attacker. This matches "Critical - direct theft of shielded or in-flight user funds" / "executing calls or moving assets a wallet owner or prover never authorised" — the wallet owner authorized the `ops` but never authorized who receives the leftover balance, and the attacker (not the signer, not a relay they chose) captures it. Repeatable for every `EmporiumStack` signature the attacker can observe before its `emporiumMessage` is consumed.

### Likelihood Explanation
Preconditions: the attacker must observe/harvest a valid signed `EmporiumStack` before it's consumed on-chain (e.g., from mempool, a relay's public API, or any leaked/rebroadcast payload), must front-run the legitimate submission (win the `usedMessages[emporiumMessage]` race), and must have their own deposited UTXOs/proof plus knowledge of the token/amount the ops will leave as a residual. This is feasible for anyone monitoring pending Emporium transactions, at the cost of generating one proof and paying gas to front-run — well within an unprivileged EOA's capability, matching the threat model (own funds, own proof, no privileged role required).

### Recommendation
Bind `stealthAddressStructure` (and ideally `rootHashHinkal`/`erc20TokenAddresses`/`amountChanges`, or at minimum a hash restricting who may redeem the residual) into the EIP-712 struct hashed under `EMPORIUM_SIGNATURE_TYPEHASH`, so the wallet owner explicitly authorizes the destination and expected token accounting for the residual UTXO, not just the raw `ops`. Alternatively, require that the residual UTXO destination is derived deterministically from `stack.signerAddress` (or a destination they separately sign), and/or restrict `runAction`'s `circomData.originalSender`/proof submitter to be the same party the signer intended (e.g., check `msg.sender`/`originalSender` against a signed relayer/prover address in the `EmporiumSignature`).

### Proof of Concept
Foundry test plan (proof generation via snarkjs harness already used in repo tests):
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable`, a mock `IHinkalWallet` for the victim, and a mock ERC20.
2. Victim deposits/holds funds in their `IHinkalWallet`; victim signs an `EmporiumStack` (`ops` = transfer tokens from wallet into Emporium contract, `emporiumMessage = M`, `maxFee`, `deadline`) per `EMPORIUM_SIGNATURE_TYPEHASH`.
3. Attacker (separate EOA, previously deposited their own UTXO into Hinkal) builds `CircomData` with: `externalActionData.externalActionMetadata = abi.encode(stack)` (harvested, unmodified `v,r,s,signerAddress,ops,maxFee,deadline,emporiumMessage=M`), attacker's own `rootHashHinkal`/`inputNullifiers`/`outCommitments`, `erc20TokenAddresses`/`amountChanges` reflecting the expected residual, and `stealthAddressStructure` = attacker's own stealth address.
4. Generate a valid snarkjs proof for the attacker's own witness satisfying `formInputNormal`'s public inputs.
5. Call `Hinkal.transact(a,b,c,dimensions,circomData)` from the attacker's EOA before the victim/relay submits their own transaction with the same `emporiumMessage`.
6. Assert: `usedMessages[M] == true`; victim's wallet balance decreased per `ops`; the resulting on-chain/off-chain UTXO commitment (from `outCommitments`/`onChainCommitments`) is spendable using the **attacker's** `nullifyingPrivateKey` (i.e., attacker can later submit a normal `transact` spending it); and the legitimate victim-originated submission with the same `emporiumMessage` now reverts with `UsedMessage`.
7. Equality check: assert `outUtxo.stealthAddressStructure == attacker's stealth address` while `stack.signerAddress == victim's wallet`, demonstrating the destination is decoupled from the signer's authorization.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L91-151)
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-340)
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
```

**File:** contracts/CircomDataBuilder.sol (L180-201)
```text
    function formBasicInput(
        uint256 chainId,
        address verifyingContract,
        CircomData calldata circomData,
        uint256[] memory input,
        uint256 index,
        uint256 emporiumMessage
    ) internal pure returns (uint256[] memory) {
        // 1) First we list public inputs as in the body of the main template (not the one with exact dimensions)
        input[index++] = circomData.stealthAddressStructure.H1x;
        input[index++] = circomData.stealthAddressStructure.H1y;
        input[index++] = circomData.stealthAddressStructure.stealthAddress;
        input[index++] = emporiumMessage; // this is for Emporium message signature verification

        // 2) Then we list the private inputs as in the body of the main template
        input[index++] = circomData.rootHashHinkal;
        input[index++] = getSignedMessageHash(
            chainId,
            verifyingContract,
            circomData,
            emporiumMessage
        );
```

**File:** contracts/HinkalHelper.sol (L208-236)
```text
    function performHinkalChecks(
        CircomData calldata circomData,
        Dimensions calldata dimensions,
        address sender
    ) external view returns (uint256[] memory) {
        require(
            (circomData.originalSender == address(0) &&
                circomData.relay != address(0)) ||
                (circomData.originalSender == sender &&
                    circomData.relay == address(0)),
            "invalid value for originalSender"
        );

        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
        );
        relayerIsValid(circomData.relay);
        dimensionsCheck(circomData, dimensions);
        checkOnchainCreation(circomData);

        return
            CircomDataBuilder.formInputForCircom(
                block.chainid,
                hinkalAddress,
                circomData
            );
    }
```

**File:** contracts/Hinkal.sol (L30-86)
```text
    function transact(
        uint256[2] calldata a,
        uint256[2][2] calldata b,
        uint256[2] calldata c,
        Dimensions calldata dimensions,
        CircomData calldata circomData
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

        {
            if (circomData.hookData.preHookContract != address(0)) {
                IPreTransactHook transactHook = IPreTransactHook(
                    circomData.hookData.preHookContract
                );
                transactHook.preTransact(circomData);
            }

            UTXO[] memory utxoSet;

            uint256[] memory oldBalances = getBalancesForArray(
                circomData.erc20TokenAddresses
            );

            if (circomData.externalActionData.externalActionId == 0) {
                _internalTransact(circomData);
            } else {
                utxoSet = _externalTransact(circomData);
            }
```

**File:** contracts/Hinkal.sol (L97-146)
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
```
