### Title
Unauthenticated Emporium calls via `signerAddress==address(0)` + zero-token Min circuit path allow arbitrary `endpoint.call(callData)` as Emporium's identity - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
When `dimensions.tokenNumber==0` and the external action is `HINKAL_EMPORIUM_ACTION_ID`, `CircomDataBuilder.formInputForCircom` routes to `formInputEmporiumMin`, whose only circuit (`MainEVMCircuitMin`) constrains solely `message == Poseidon(messageSeed)` and leaves `calldataHash` as an unconstrained public signal. `EmporiumUpgradeable.verifyWallet` skips all signature verification when `stack.signerAddress == address(0)`, checking only replay via `usedMessages`. Combined, any unprivileged party can force `EmporiumUpgradeable.runAction` to execute an arbitrary `op.endpoint.call{value: op.value}(op.callData)` with `msg.sender == Emporium`, without owning shielded funds, a wallet key, or any Emporium authorization.

### Finding Description
The broken equality: the set of values the SNARK/on-chain checks actually bind (`emporiumMessage == Poseidon(messageSeed)`, `timeStamp`, `calldataHash`) is expected to equal the set of values `runAction` acts on (`op.endpoint`, `op.callData`, `op.value`, `stack.signerAddress`) — but it does not.

- `formInputForCircom` selects `formInputEmporiumMin` whenever `externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0`: [1](#0-0) 
- `formInputEmporiumMin` only feeds `[emporiumMessage, timeStamp, calldataHash]` to the verifier: [2](#0-1) 
- `MainEVMCircuitMin` only constrains `message <== Poseidon(messageSeed)`; `calldataHash` is declared as a public input but never used in any constraint: [3](#0-2) 
- The only on-chain tie to `calldataHash` is an integrity check (`getHashedCalldata(circomData) == circomData.calldataHash`) that just prevents tampering between proof creation and execution — it does not verify that any legitimate party authorized the encoded `endpoint`/`callData`: [4](#0-3) 
- `EmporiumUpgradeable.verifyWallet` performs **no signature check at all** when `stack.signerAddress == address(0)`, only marking `usedMessages` for replay protection: [5](#0-4) 
- `runAction` then executes the stateless branch `op.endpoint.call{value: op.value}(op.callData)` with `msg.sender == Emporium`, gated only by an endpoint-selector blacklist for wallet-hijacking selectors: [6](#0-5) 

With `tokenNumber==0`, `dimensionsCheck` requires all the token/nullifier/commitment arrays to be empty/zero (trivially satisfiable), so no root, nullifier, or spend authorization is needed anywhere in the path: [7](#0-6) . The attacker only needs a self-generated Poseidon proof for an arbitrary `messageSeed` they pick themselves — no secret material, key, or prior deposit is required. `onlyAllowedRecipient` only checks that the *caller of `runAction`* is `Hinkal` itself, not who initiated the top-level `transact` call: [8](#0-7) . Thus no existing guard prevents an arbitrary unprivileged EOA from driving this call.

### Impact Explanation
Emporium's identity (`msg.sender`) is used to invoke arbitrary contracts with arbitrary calldata, chosen entirely by the attacker, with zero cost or knowledge of any secret. If Emporium holds any residual ERC20/ETH balance or has any outstanding token approvals granted to it by other integrated protocols (a realistic scenario for a stateless multi-step "batch" contract like Emporium), an attacker can direct calls (e.g., `transferFrom(Emporium, attacker, amount)` on an approved spender, or any arbitrary logic on a "victim" contract that trusts `msg.sender == Emporium`) that were never authorized by any wallet owner or prover. This matches the "executing calls or moving assets a wallet owner or prover never authorised" High-severity category, with a path toward theft of any assets/approvals actually held by Emporium (Critical if realized funds are present).

### Likelihood Explanation
- Preconditions: Emporium must be registered as `HINKAL_EMPORIUM_ACTION_ID` in `Hinkal`'s action map (standard deployment configuration), and the attacker must call `transact` with `dimensions.tokenNumber==0` and `erc20TokenAddresses.length==0`.
- Attacker cost: trivial — one self-chosen `messageSeed`, one Poseidon proof generation (no circomlib/root/nullifier knowledge required), one arbitrary `EmporiumStack` with `signerAddress=address(0)`.
- Repeatable per unique `emporiumMessage` (bounded only by `usedMessages` replay protection, which the attacker can trivially avoid by picking a fresh `emporiumMessage`/`messageSeed` each time).
- Whether the impact materializes as fund theft depends on Emporium actually holding value/approvals at attack time; the call-execution primitive itself is always achievable regardless.

### Recommendation
- Require a real authorization even when `stack.signerAddress == address(0)`: bind `calldataHash`/`op.endpoint`/`op.callData`/`op.value` into an in-circuit constraint (not just an off-chain-computed integrity hash) so the ZK proof itself commits to what will execute, and require that this proof-carrying commitment can only be produced by someone with legitimate spend authority (e.g., tie it to consumed nullifiers/root when tokens are involved, or a dedicated "self-service"/"no-signer" mode must not permit calling arbitrary third-party endpoints with Emporium as `msg.sender`).
- Alternatively, disallow the `signerAddress == address(0)` stateless branch entirely for `HINKAL_EMPORIUM_ACTION_ID` when `erc20TokenAddresses.length == 0`, or restrict `op.endpoint` to an allow-list when no signer/no funds are involved.
- Ensure `MainEVMCircuitMin`'s `calldataHash` signal is actually constrained (e.g., hashed together with `message`) rather than being a free/unused public input.

### Proof of Concept
Foundry fork test plan:
1. Deploy/point at real `Hinkal`, `HinkalHelper`, `VerifierFacade`, and `EmporiumUpgradeable` (registered for `HINKAL_EMPORIUM_ACTION_ID`); optionally fund Emporium with a token balance/approval to simulate "assets held" to demonstrate impact.
2. Deploy a `VictimContract` with a state-changing function (e.g., `pull()`/`transferFrom`) as `endpoint`.
3. Off-chain, pick random `messageSeed`, compute `message = Poseidon(messageSeed)` via snarkjs, generate a valid Groth16 proof for `MainEVMCircuitMin` with public inputs `[message, timeStamp, calldataHash]`.
4. Build `CircomData` with `dimensions.tokenNumber=0`, `erc20TokenAddresses=[]`, `externalActionData.externalActionId=HINKAL_EMPORIUM_ACTION_ID`, `externalActionMetadata = abi.encode(EmporiumStack{signerAddress:address(0), ops:[{endpoint:victim, invokeWallet:false, value:0, callData:arbitraryCall}], maxFee:0, deadline:0})`, and `calldataHash = getHashedCalldata(circomData)` (self-consistent, no external authorization).
5. Call `Hinkal.transact(...)` as an unprivileged EOA.
6. Assert: (a) the call to `VictimContract` executed with `msg.sender == address(Emporium)`; (b) `circomData.externalActionData.externalActionMetadata`'s `op.callData`/`op.endpoint` never appeared in `formInputEmporiumMin`'s output vector fed to the verifier; (c) no `usedMessages`/nullifier/root check tied to a legitimate signer was performed before the call executed.

### Citations

**File:** contracts/CircomDataBuilder.sol (L139-148)
```text
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
```

**File:** contracts/CircomDataBuilder.sol (L150-161)
```text
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

**File:** circuits/MainEVMCircuitMin.circom (L6-17)
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
```

**File:** contracts/HinkalHelper.sol (L64-171)
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

        require(
            circomData.encryptedOutputs.length == dimensions.tokenNumber,
            "EncryptedOutputs number should be equal to token number"
        );

        uint previousEncryptedOutputAmount = circomData
            .encryptedOutputs
            .length > 0
            ? circomData.encryptedOutputs[0].length
            : 0;

        for (uint i = 0; i < circomData.encryptedOutputs.length; i++) {
            require(
                circomData.encryptedOutputs[i].length ==
                    previousEncryptedOutputAmount,
                "Encrypted output amount should be equal"
            );

            for (uint j = 0; j < circomData.encryptedOutputs[i].length; j++) {
                require(
                    circomData.encryptedOutputs[i][j].length > 0,
                    "Missing encrypted output for off-chain commitment"
                );
            }
        }

        require(
            previousEncryptedOutputAmount == dimensions.outputAmount,
            "Actual and Claimed Encrypted Output Amount should be equal"
        );

        require(
            circomData.onChainEncryptedOutput.length > 0,
            "Missing encrypted output for on-chain commitment"
        );

        require(
            circomData.stealthAddressStructure.H0x != 0,
            "H0x cannot be zero"
        );

        require(
            circomData.feeStructure.variableRate <= 10000,
            "Variable rate cannot be greater than 10000"
        );
    }
```

**File:** contracts/HinkalHelper.sol (L221-225)
```text
        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
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
