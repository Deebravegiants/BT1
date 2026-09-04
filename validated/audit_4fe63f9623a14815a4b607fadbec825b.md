### Title
Emporium fund-moving calldata (`EmporiumOperation.endpoint/value/callData`) escapes all circuit constraints via `dimensions.tokenNumber=0` routing to `MainEVMCircuitMin` - ([File: circuits/MainEVMCircuitMin.circom])

### Summary
`Hinkal.transact` selects the verifier solely from `VerifierFacade.buildVerifierId(dimensions, externalActionId)`, a hash of `(tokenNumber, nullifierAmount, outputAmount, externalActionId)`. When an attacker sets `dimensions.tokenNumber = 0` for the Emporium action, `CircomDataBuilder.formInputForCircom` routes to `formInputEmporiumMin`, which only submits `(emporiumMessage, timeStamp, calldataHash)` as public signals, matching `MainEVMCircuitMin`, a template that has zero constraints on any signal. The real fund movement happens later inside `EmporiumUpgradeable.runAction`, which decodes `externalActionData.externalActionMetadata` into an `EmporiumStack` and executes attacker-supplied `ops` (`endpoint`, `value`, `callData`) - fields that no circuit (neither `MainEVMCircuitMin` nor `MainEVMCircuit`) ever constrains, and that are authorized only by an EIP-712 signature check that is skipped entirely when `stack.signerAddress == address(0)`.

### Finding Description
Equality that should hold: *verifierId chosen by `buildVerifierId(dimensions, externalActionId)`* == *the circuit whose constraints cover every field the transaction acts upon*. It does not hold for the Emporium-min path.

Trace:
- `Hinkal.transact` computes `buildVerifierId(dimensions, circomData.externalActionData.externalActionId)` and uses it to pick the verifier: `contracts/Hinkal.sol:44-56`, `contracts/VerifierFacade.sol:28-43`.
- `HinkalHelper.performHinkalChecks` calls `dimensionsCheck`, which forces `erc20TokenAddresses.length == amountChanges.length == inputNullifiers.length == outCommitments.length == dimensions.tokenNumber` (`contracts/HinkalHelper.sol:64-90`). With `tokenNumber=0` all of these arrays are empty - there is no `amountChanges`/nullifier/commitment accounting at all for this call.
- `CircomDataBuilder.formInputForCircom` special-cases `externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0` and returns only 3 public signals (`emporiumMessage`, `timeStamp`, `calldataHash`) via `formInputEmporiumMin` (`contracts/CircomDataBuilder.sol:134-161`).
- `circuits/MainEVMCircuitMin.circom` declares `outTimeStamp`, `calldataHash` as public inputs and `message <== Poseidon(1)([messageSeed])` as the only constraint. Neither `outTimeStamp` nor `calldataHash` appears in any equation - they are free, unconstrained public inputs. The attacker (who generates their own proof for their own action) can choose `messageSeed` freely and thus trivially produce a valid proof for **any** `calldataHash`/`timeStamp` value they put in `circomData`.
- Real value movement happens in `_externalTransact` → `EmporiumUpgradeable.runAction` (`contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol:76-160`), which decodes `externalActionMetadata` into `EmporiumStack{ v, r, s, signerAddress, ops[], maxFee, deadline }` and, for each `op`, either calls the user's own `HinkalWallet` (Case 1, when `invokeWallet && signerAddress != 0`) or does a raw `op.endpoint.call{value: op.value}(op.callData)` directly from the Emporium contract (Case 2, stateless).
- Authorization of `ops` is done by `verifyWallet` (`EmporiumUpgradeable.sol:302-349`), which recovers a signer from an EIP-712 hash over `_hashEmporiumOps(stack.ops)` **only if `stack.signerAddress != address(0)`**. If `signerAddress == address(0)`, `verifyWallet` just marks the message used and **returns immediately with no signature check at all**.
- The `calldataHash` check in `HinkalHelper.performHinkalChecks` (`require(CircomDataBuilder.getHashedCalldata(circomData) == circomData.calldataHash)`) is a self-consistency check computed from data the attacker themselves supplies in the very same transaction (`originalSender == msg.sender` when not using a relay); it cannot constrain what an *independent* party approved, because there is no independent party here - the attacker is both prover and caller.

Net result: for `dimensions.tokenNumber=0` + Emporium action + `EmporiumStack.signerAddress = address(0)`, the entire authorization chain for `EmporiumOperation.endpoint/value/callData` collapses to nothing cryptographically binding - no circuit constrains these fields (true even for the full `MainEVMCircuit`, since neither circuit template has any signal for `externalActionMetadata`/`ops`), and the one off-circuit signature gate (`verifyWallet`) is bypassed by choosing `signerAddress = address(0)`. `runAction`'s stateless branch only blocks calling the `callHinkalWallet`/`doSendToRelay` selectors directly (`EmporiumUpgradeable.sol:104-110`); any other `endpoint`/`callData`/`value` is executed as `msg.sender = EmporiumUpgradeable`, spending whatever native ETH balance the Emporium contract itself holds.

### Impact Explanation
An unprivileged attacker can force execution of arbitrary external calls (`endpoint.call{value}(callData)`) as the Emporium contract, spending ETH out of the Emporium contract's own balance, with:
- no ZK constraint on any of `endpoint`, `value`, `callData` (neither `MainEVMCircuit` nor `MainEVMCircuitMin` has signals for these fields),
- no EIP-712 authorization (bypassed via `signerAddress = address(0)`),
- the only gates being `onlyAllowedRecipient`/`externalActionMap` (which just check the action is registered and public - satisfied by any caller through `Hinkal.transact`) and the narrow selector blocklist.

This is a proof/authorization-coverage bypass: fund-moving calldata (`ops`) runs entirely unconstrained by any circuit and, in the `signerAddress=0` branch, unconstrained by any signature either. Whether this reaches "Critical - direct theft of shielded funds" depends on whether the Emporium contract accrues a spendable native-ETH balance in practice (e.g., dust left over from prior swaps/fills that isn't swept back because `handleOut` only sweeps balances for `circomData.erc20TokenAddresses` entries present in *that* transaction, and `tokenNumber=0` means none are present to sweep). At minimum this is a High-severity "executing calls a wallet owner/prover never authorized" issue (arbitrary call execution as the Emporium contract with a trivial, self-satisfiable proof); it escalates to Critical if the Emporium contract holds any meaningful ETH balance at the time of attack, since that balance can be drained via `op.value` with zero authorization.

### Likelihood Explanation
- Preconditions: `HINKAL_EMPORIUM_ACTION_ID` must be registered and reachable (already true for normal Emporium usage), attacker needs to be able to generate a valid Groth16 proof for `MainEVMCircuitMin` — trivial since it is unconstrained apart from `message = Poseidon(messageSeed)`, which the attacker computes themselves.
- Attacker cost: one `Hinkal.transact` call with `dimensions = (0, x, y)`, a self-generated trivial proof, and a crafted `EmporiumStack{signerAddress: address(0), ops: [...]}`.
- Repeatable per transaction; limited by whatever balance/target state the attacker wants to act on via the arbitrary call each time.
- Full quantification of "funds stolen" requires confirming the Emporium contract's residual ETH balance in a realistic deployment/fork, which needs a Foundry/fork PoC as required by the rules.

### Recommendation
- Do not allow `dimensions.tokenNumber == 0` to route to a verifier (`MainEVMCircuitMin`) that has zero relationship to `externalActionData.externalActionMetadata`/`EmporiumOperation` fields unless the metadata itself is bound by a mandatory, non-bypassable authorization (e.g., always require and verify `stack.signerAddress != address(0)` and a valid EIP-712 signature over `ops` in `EmporiumUpgradeable.verifyWallet`, removing the `signerAddress == address(0)` early return).
- Alternatively, include a commitment to `externalActionData.externalActionMetadata` (or at least `keccak256(ops)`) as a public circuit signal that is constrained (e.g., forced equal to a signal derived on-chain) in both `MainEVMCircuit` and `MainEVMCircuitMin`, so `buildVerifierId`'s selected circuit always covers every acted-upon field, closing the coverage gap the current `calldataHash`-only Solidity check leaves for self-authored transactions.
- Ensure the Emporium contract never retains a spendable native-ETH (or token) balance across transactions (sweep to zero at end of every `runAction`), removing the asset that this unauthorized-call primitive could drain.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `VerifierFacade` (register the real `mainEVMCircuitMin0v4` verifier for the `buildVerifierId(Dimensions(0, n, m), HINKAL_EMPORIUM_ACTION_ID)` id), and `EmporiumUpgradeable`, registering it in `externalActionMap[HINKAL_EMPORIUM_ACTION_ID]`.
2. Fund the Emporium contract with a nonzero ETH balance (simulating residual dust from a prior legitimate transaction) via `vm.deal(address(emporium), 1 ether)`.
3. As an attacker EOA (not owner/admin/relay), construct `Dimensions{tokenNumber: 0, nullifierAmount: n, outputAmount: m}` and a `CircomData` with empty `erc20TokenAddresses`/`amountChanges`/`inputNullifiers`/`outCommitments`, `externalActionData = {externalAddress: emporium, externalActionId: HINKAL_EMPORIUM_ACTION_ID, externalActionMetadata: abi.encode(EmporiumStack{signerAddress: address(0), ops: [EmporiumOperation{endpoint: attackerTarget, invokeWallet: false, value: 1 ether, callData: ""}], maxFee:0, deadline: block.timestamp+1})}`.
4. Set `calldataHash = CircomDataBuilder.getHashedCalldata(circomData)` (self-satisfiable since attacker controls all fields), generate a real Groth16 proof for `MainEVMCircuitMin` with an arbitrary `messageSeed` such that `message == circomData.emporiumMessage`.
5. Call `Hinkal.transact(a,b,c,dimensions,circomData)`.
6. Assert: (a) `CircomDataBuilder.formInputForCircom(...)` returns a 3-element array (`length == 3`); (b) the transaction succeeds and `attackerTarget` receives `1 ether` pulled from the Emporium contract's balance, with `EmporiumUpgradeable.verifyWallet` never checking any ECDSA signature (assert via event/trace that `stack.v/r/s` are never validated); (c) confirm no signal in the verified public-input vector or in `MainEVMCircuitMin.circom`'s constraint set corresponds to `op.endpoint`, `op.value`, or `op.callData`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7) [9](#0-8) 

Note on unresolved detail: I was unable to retrieve the exact body of `CircomDataBuilder.getHashedCalldata` (a tool error prevented reading `contracts/CircomDataBuilder.sol` lines 1-60) to confirm precisely which `CircomData` fields it hashes. This does not change the core finding, since the attacker is the transaction's own author and can always make this self-computed hash check pass regardless of its exact coverage - but a full audit should independently verify `getHashedCalldata`'s field list.

### Citations

**File:** contracts/VerifierFacade.sol (L28-43)
```text
    function buildVerifierId(
        Dimensions calldata dimensions,
        uint256 externalActionId
    ) public pure returns (uint256) {
        return
            uint256(
                keccak256(
                    abi.encode(
                        dimensions.tokenNumber,
                        dimensions.nullifierAmount,
                        dimensions.outputAmount,
                        externalActionId
                    )
                )
            );
    }
```

**File:** contracts/Hinkal.sol (L36-56)
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-118)
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

**File:** contracts/external-actions/emporium/EmporiumStack.sol (L1-19)
```text
// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.17;

struct EmporiumOperation {
    address endpoint;
    bool invokeWallet;
    uint128 value;
    bytes callData;
}

struct EmporiumStack {
    uint8 v;
    bytes32 r;
    bytes32 s;
    address signerAddress;
    EmporiumOperation[] ops;
    uint256 maxFee;
    uint256 deadline;
}
```
