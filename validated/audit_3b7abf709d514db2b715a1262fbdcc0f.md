### Title
EmporiumUpgradeable output UTXO destination (`stealthAddressStructure`) is not bound by the victim's EIP-712 `EmporiumSignature`, allowing theft of wallet-generated fund inflows - (`contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.verifyWallet` only signs over `emporiumMessage`, the hash of `stack.ops`, `maxFee`, and `deadline` [1](#0-0) . It never includes `circomData.stealthAddressStructure`, `circomData.erc20TokenAddresses`, `deltaAmountChanges`, `circomData.relay`, or `circomData.feeStructure` in the signed payload. Since `handleOut` creates the resulting UTXO using `circomData.stealthAddressStructure`, which is completely decoupled from the wallet owner's signature, whoever actually submits the `Hinkal.transact` call (any permissionless caller) chooses who owns the newly created shielded output — not the signer whose wallet performed the operation.

### Finding Description
Broken equality: (destination stealth address that receives the UTXO produced by a signer-authorized wallet operation) should equal (a value chosen or approved by `stack.signerAddress`), but instead equals (whatever `circomData.stealthAddressStructure` the *caller* of `Hinkal.transact` supplies), which is unconstrained by the EIP-712 signature.

Trace:
- `Hinkal.transact` is fully permissionless; any address can call it as long as `performHinkalChecks` and `verifyProof` pass [2](#0-1) .
- `dimensions.nullifierAmount` can legitimately be `0` (`dimensionsCheck` only requires the per-token nullifier arrays to have a *consistent* length, not a non-zero one) [3](#0-2) , meaning the flow can proceed without spending any existing shielded UTXO — appropriate for the "wallet operation" (Case 1, `invokeWallet`) path where the input funds come from the signer's `HinkalWallet` contract, not from a nullified note.
- `_externalTransact` calls `EmporiumUpgradeable.runAction` as `msg.sender == Hinkal` (the only address registered via `onlyAllowedRecipient`) [4](#0-3) [5](#0-4) . The attacker never needs to be an "allowed recipient" themselves — they only need to be the (permissionless) caller of `Hinkal.transact`.
- Inside `runAction`, `stack.ops` (signed by the victim) are replayed *verbatim* via `verifyWallet`, so the attacker cannot alter what operations execute — they must faithfully replay the victim's authorized calls, e.g. a swap executed through the victim's `HinkalWallet` [6](#0-5) .
- After the ops run, `handleOut` sends the resulting positive `balanceChange` to `msg.sender` (Hinkal, which will re-derive and enforce the balance/UTXO accounting) and creates the output UTXO using `circomData.stealthAddressStructure` [7](#0-6)  — a field the attacker fully controls and which was never part of the signed `EmporiumSignature`.
- `payRelayFees` skips fee-charging whenever `deltaAmountChanges[i] >= 0` ("tokens deposited into Emporium are not charged") [8](#0-7) , so an attacker structuring the call as a "deposit" of the swap's output avoids fees while still stealing the resulting UTXO.
- Back in `Hinkal.transact`, the balance/UTXO accounting (`balanceDif == amountChanges[i] + utxoAmount`) only checks aggregate token conservation, not ownership of the resulting UTXO [9](#0-8) , so this guard does not prevent the attacker from being the beneficiary.
- On the circuit side, `outPublicKeys`/`outStealthAddress` used for the *output* commitment are private witness inputs supplied by whoever generates the proof, and are unconstrained relative to the `EmporiumSignature`/`spendingPublicKey` used for spending existing notes (`eddsaSignature`/`spendingPublicKey` only govern *input* note ownership when `nullifierAmount > 0`) [10](#0-9) . With `nullifierAmount == 0`, no proof of note ownership is required at all, so the attacker can freely generate a proof for their own `stealthAddressStructure`.

Why existing guards fail: `verifyWallet`'s EIP-712 signature scope is too narrow (it authorizes *what actions run*, not *who receives the resulting value*); `onlyAllowedRecipient` only restricts the caller of `runAction` to the Hinkal contract itself, not the ultimate beneficiary of the created UTXO; `performHinkalChecks`/`dimensionsCheck`/`calldataHash` integrity checks only ensure self-consistency of the calldata the attacker submits, not that it matches what the victim intended for fund destination; and the balance-equality checks in `Hinkal.transact` are purely arithmetic, agnostic to UTXO ownership.

### Impact Explanation
Any relay, MEV bot, or party who observes/receives a victim's signed `EmporiumStack` payload (which is by design meant to be handed off to a third party — a relay — for submission, given the `relay`/fee-payment plumbing) can resubmit the same signed `stack.ops` but swap in their own `stealthAddressStructure`, redirecting the entire output of the wallet-authorized operation (e.g., swap proceeds) into an attacker-owned shielded UTXO. This is direct theft of in-flight user funds generated by a signature the user believed only authorized specific *actions*, not a change of *beneficiary*. This matches the Critical category: "direct theft of shielded or in-flight user funds." It is repeatable for every signed `EmporiumStack` an attacker can intercept, and costs the attacker only gas plus proof generation (trivial for `nullifierAmount == 0`).

### Likelihood Explanation
Preconditions: a victim must have produced a signed `EmporiumSignature`/`EmporiumStack` intended for third-party submission (a standard pattern given the relay-fee-payment logic built into `payRelayFees`/`sendToRelayFromWallet`), and an attacker must intercept it before/instead of the intended submitter. This is entirely plausible in a relay-based or mempool-visible submission model, requires no privileged role, no compromised keys, and no assumption beyond normal usage of the signature-relay pattern that the contract itself implements. The attacker's cost is minimal (gas + a permissionless proof for zero input notes).

### Recommendation
Include `circomData.stealthAddressStructure` (and ideally `erc20TokenAddresses`, `feeStructure`, and `relay`) in the EIP-712 `EmporiumSignature` payload signed by `stack.signerAddress`, so the signer explicitly authorizes both the actions *and* the destination/terms of the resulting funds. Recompute `EMPORIUM_SIGNATURE_TYPEHASH` and `verifyWallet`'s hashed struct to bind these fields cryptographically.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable` (with Hinkal registered as `allowedRecipient`), a mock swap `endpoint`, and a `HinkalWallet` owned/controlled by `victim`.
2. Victim signs an `EmporiumStack` (`EMPORIUM_SIGNATURE_TYPEHASH`) authorizing a single op: `invokeWallet=true`, calling `endpoint` to perform a token swap that sends output tokens to the Emporium contract's balance.
3. Attacker crafts `circomData` with:
   - `externalActionData.externalActionMetadata = abi.encode(stack)` (using the victim's untouched, validly-signed `stack.ops`/`v`/`r`/`s`),
   - `stealthAddressStructure` set to attacker's own keys,
   - `dimensions.nullifierAmount = 0` (no input notes spent),
   - a proof generated locally by the attacker (trivial for zero-input dimension) matching `calldataHash`.
4. Attacker calls `Hinkal.transact(...)` directly (`originalSender = attacker`, `relay = address(0)`).
5. Assert: (a) the swap executes exactly as victim authorized (op call succeeded, funds moved from victim's `HinkalWallet`), (b) the resulting `UTXO`/on-chain commitment inserted into the tree has a stealth address/commitment that decrypts under the **attacker's** `nullifyingPrivateKey`, not the victim's, (c) `payRelayFees` charged no fee (deposit branch), confirming the victim's authorized action's proceeds landed entirely under attacker control.

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L210-214)
```text
        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            // tokens deposited into Emporium are not charged
            if (deltaAmountChanges[i] >= 0) {
                continue;
            }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L318-328)
```text
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
```

**File:** contracts/Hinkal.sol (L30-65)
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
```

**File:** contracts/Hinkal.sol (L96-146)
```text
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

**File:** contracts/HinkalHelper.sol (L92-104)
```text
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
```

**File:** contracts/external-actions/ExternalActionBaseUpgradeable.sol (L39-46)
```text
    modifier onlyAllowedRecipient() {
        ExternalActionBaseStorage storage $ = _getExternalActionBaseStorage();
        require(
            $._isAllowedRecipient[msg.sender],
            "ExternalActionBase: sender not allowed"
        );
        _;
    }
```

**File:** circuits/MainEVMCircuit.circom (L100-169)
```text
	for (var i = 0; i < tokenCount; i++) {
      // 0) iterate over all token types
      var inTotal = 0;
      var outTotal = 0;

      for(var j=0; j< inputCount; j++) {

        calcInPublicKeys[i][j] = StealthAddressCalculator();
        calcInPublicKeys[i][j].spendingPublicKey <== spendingPublicKey;
        calcInPublicKeys[i][j].nullifyingPrivateKey <== nullifyingPrivateKey;
        calcInPublicKeys[i][j].nullifyingPrivateKeyBits <== nullifyingPrivateKeyBits.out;
        calcInPublicKeys[i][j].H0Ax <== inH0Ax[i][j];
        calcInPublicKeys[i][j].H0Ay <== inH0Ay[i][j];

        // 1) Calculating Commitments for Input UTXOs
        calcCommitment[i][j] = OriginalCommitmentCalculator();
        calcCommitment[i][j].amount <== inAmounts[i][j];
        calcCommitment[i][j].erc20TokenAddress <== erc20TokenAddresses[i];
        calcCommitment[i][j].publicKey <== calcInPublicKeys[i][j].out;
        calcCommitment[i][j].timeStamp <== inTimeStamps[i][j];

        preventInOverflow[i][j] = OverflowPreventer(inputCount);
        preventInOverflow[i][j].in <== inAmounts[i][j];

        // 2) Calculating Nullifier from commitment and signature
        calcSignature[i][j] = Signature();
        calcSignature[i][j].nullifyingPrivateKey <== nullifyingPrivateKey;
        calcSignature[i][j].commitment <== calcCommitment[i][j].out;

        calcNullifier[i][j] = NullifierCalculator();
        calcNullifier[i][j].commitment <== calcCommitment[i][j].out;
        calcNullifier[i][j].signature <== calcSignature[i][j].out;

        // 3) Checking that nullifier is legit
        inNullifiers[i][j] === calcNullifier[i][j].out;

        // 4) Calculating Transaction Root Hash
        calcTransactionRootHash[i][j] = MerkleRootCalculator(treeDepth);
        calcTransactionRootHash[i][j].inCommitment <== calcCommitment[i][j].out;
        for (var k = 0; k < treeDepth; k++) {
          calcTransactionRootHash[i][j].commitmentSiblings[k] <== inCommitmentSiblings[i][j][k];
          calcTransactionRootHash[i][j].commitmentSiblingSides[k] <== inCommitmentSiblingSides[i][j][k];
        }

        // 5) Checking that transaction root hash is legit
        calcEqual[i][j] = ForceEqualIfEnabled();
        calcEqual[i][j].in[0] <== calcTransactionRootHash[i][j].rootHash;
        calcEqual[i][j].in[1] <== rootHashHinkal;
        calcEqual[i][j].enabled <== inAmounts[i][j];
        inTotal += inAmounts[i][j];
      }

    for(var j=0; j< outputCount; j++) {
      calcOutCommitment[i][j] = OriginalCommitmentCalculator();
      calcOutCommitment[i][j].amount <== outAmounts[i][j]; // if outAmount is negative, than this line will throw error
      calcOutCommitment[i][j].erc20TokenAddress <== erc20TokenAddresses[i];
      calcOutCommitment[i][j].publicKey <== outPublicKeys[i][j];
      calcOutCommitment[i][j].timeStamp <== outTimeStamp;

      // Checking that output commitment is legit
      calcOutCommitment[i][j].out === outCommitments[i][j];

      preventOutOverflow[i][j] = OverflowPreventer(outputCount);
      preventOutOverflow[i][j].in <== outAmounts[i][j];
      outTotal += outAmounts[i][j];
    }

      // for each token type, the sum of refund and swapped amount should be equal to the sum of input amounts
      inTotal + amountChanges[i] === outTotal;
	}
```
