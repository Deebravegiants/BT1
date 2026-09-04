### Title
Emporium `runAction` allows unauthorized arbitrary calls with unbacked proofs when `erc20TokenAddresses` is empty - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol, circuits/MainEVMCircuitMin.circom)

### Summary
When a transaction targets `HINKAL_EMPORIUM_ACTION_ID` with an empty `erc20TokenAddresses` array, `CircomDataBuilder.formInputForCircom` routes proof-input construction to `formInputEmporiumMin`, which is checked against `MainEVMCircuitMin` [1](#0-0) . That circuit performs **no** ownership/authorization check at all — it only computes `message <== Poseidon(1)([messageSeed])` from a completely free private input, with no EdDSA signature, no nullifier check, and no Merkle-root check [2](#0-1) . Any unprivileged party can therefore construct a trivially satisfying Groth16 witness for arbitrary public inputs (`emporiumMessage`, `timeStamp`, `calldataHash`).

### Finding Description
`Hinkal.transact` gates execution solely on `verifyProof` succeeding for the verifier selected by `buildVerifierId(dimensions, externalActionId)` [3](#0-2) . For the Emporium-min path (`erc20TokenAddresses.length == 0`), the selected circuit (`MainEVMCircuitMin`) provides no cryptographic binding to any spending key, nullifier or Merkle root — unlike the normal path where `SignatureVerifier` enforces EdDSA ownership over `signedMessageHash` (which itself is correctly bound to `chainId`/`verifyingContract` in `getSignedMessageHash`) [4](#0-3) [5](#0-4) .

Once the trivial proof passes, `Hinkal._externalTransact` invokes `EmporiumUpgradeable.runAction`, which decodes an attacker-supplied `EmporiumStack` from `circomData.externalActionData.externalActionMetadata` [6](#0-5) . If `stack.signerAddress == address(0)`, `verifyWallet` returns immediately without any signature check [7](#0-6) , and the "stateless" branch executes `op.endpoint.call{value: op.value}(op.callData)` with only a selector blacklist on `callHinkalWallet`/`doSendToRelay` [8](#0-7) .

Critically, because `circomData.erc20TokenAddresses.length == 0` in this path, the post-execution balance-equality loop (`balanceChange`/`BalanceChangeShouldBePositive` check) never executes — its bound is `circomData.erc20TokenAddresses.length`, i.e. zero [9](#0-8) . There is therefore no equality at all constraining what value the arbitrary call may move (this breaks the "value moved by Hinkal or an external action but not counted in the balance equation" invariant).

### Impact Explanation
An unprivileged EOA can:
1. Craft any `CircomData` with `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `erc20TokenAddresses = []`, and `dimensions.tokenNumber = 0`.
2. Generate a valid Groth16 proof for `MainEVMCircuitMin` for arbitrary `emporiumMessage`/`timeStamp`/`calldataHash` (no secret knowledge required).
3. Embed an `EmporiumStack` with `signerAddress = address(0)` and an `EmporiumOperation` whose `endpoint`/`callData`/`value` are fully attacker-chosen (any target except the two blacklisted selectors).
4. Call `Hinkal.transact`; the proof passes trivially, `verifyWallet` is skipped, and the arbitrary call executes from `EmporiumUpgradeable`'s own address/context, pulling native ETH held by the contract (it has a `receive()` payable fallback) with no balance-equality constraint.

This allows theft of any ETH/protocol funds held by `EmporiumUpgradeable` and unauthorized external calls made in its name, without ever owning a shielded balance or private key — a wallet/external-action call not authorized by any prover or signer. This matches the High-severity category "theft ... of protocol/relay fees" / "executing calls or moving assets ... a prover never authorised."

### Likelihood Explanation
High. No privileged role, relayer collusion, or secret material is required — only the ability to generate a Groth16 proof for a circuit with no real constraints, which is standard, permissionless tooling. The only gating conditions (`onlyAllowedRecipient`, selector blacklist) are already satisfiable through the normal `Hinkal.transact` → `_externalTransact` flow.

### Recommendation
- Require a real ownership/authorization proof (e.g., mandatory nullifier/root/signature check) for any circuit variant that can trigger arbitrary external calls, or disallow `signerAddress == address(0)` (fully unauthenticated "stateless" ops) entirely for calls with non-zero `value` / arbitrary `endpoint`.
- Do not skip the balance-equality enforcement when `erc20TokenAddresses.length == 0`; add an explicit invariant that no native-asset balance change is possible when no tokens are declared, or require `msg.value`/balance deltas to be zero-checked regardless of array length.
- Bind `calldataHash`/`emporiumMessage` cryptographically to a legitimate signer identity even on the "min" circuit path, mirroring the `getSignedMessageHash` binding used for the full circuit.

### Proof of Concept
1. Attacker builds `CircomData` with `externalActionData = {externalActionId: HINKAL_EMPORIUM_ACTION_ID, externalAddress: EmporiumUpgradeable, externalActionMetadata: abi.encode(EmporiumStack({ops: [{endpoint: attacker, invokeWallet: false, value: <EmporiumBalance>, callData: "0x"}], signerAddress: address(0), maxFee: 0, deadline: type(uint256).max, v:0, r:0, s:0}))}`, `erc20TokenAddresses = []`, matching `dimensions = {tokenNumber:0, nullifierAmount:0, outputAmount:0}`.
2. Attacker locally computes `calldataHash` via `getHashedCalldata` logic and generates a Groth16 witness/proof for `MainEVMCircuitMin` using an arbitrary `messageSeed` (unconstrained).
3. Attacker calls `Hinkal.transact(a, b, c, dimensions, circomData)`.
4. `performHinkalChecks` succeeds (calldata hash matches, relay checks pass trivially with `relay = address(0)`), `verifyProof` succeeds because the circuit has no real constraints, `_externalTransact` calls `EmporiumUpgradeable.runAction`.
5. `verifyWallet` short-circuits (`signerAddress == address(0)`), the stateless branch executes `attacker.call{value: EmporiumBalance}("0x")`, and the empty `erc20TokenAddresses` array skips all balance-equality checks — draining the contract's ETH to the attacker.

### Citations

**File:** contracts/CircomDataBuilder.sol (L97-132)
```text
    function getSignedMessageHash(
        uint256 chainId,
        address verifyingContract,
        CircomData calldata circomData,
        uint256 emporiumMessage
    ) internal pure returns (uint256) {
        // split into two encode calls to avoid "stack too deep"
        uint256 hash1 = uint256(
            keccak256(
                abi.encode(
                    chainId,
                    verifyingContract,
                    circomData.rootHashHinkal,
                    _encodeTokenAddresses(circomData.erc20TokenAddresses),
                    _encodeAmountChanges(circomData.amountChanges),
                    circomData.timeStamp,
                    _flatUint256Matrix(circomData.inputNullifiers),
                    _flatUint256Matrix(circomData.outCommitments),
                    circomData.calldataHash,
                    emporiumMessage
                )
            )
        );
        uint256 hash2 = uint256(
            keccak256(
                abi.encode(
                    circomData.stealthAddressStructure.H1x,
                    circomData.stealthAddressStructure.H1y,
                    circomData.stealthAddressStructure.H0x,
                    circomData.stealthAddressStructure.H0y
                )
            )
        );
        return
            uint256(keccak256(abi.encode(hash1, hash2))) % CIRCOM_P;
    }
```

**File:** contracts/CircomDataBuilder.sol (L134-148)
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

**File:** contracts/Hinkal.sol (L30-56)
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
```

**File:** circuits/MainEVMCircuit.circom (L91-95)
```text
  // verifying signature
  component sigVerifier = SignatureVerifier();
  sigVerifier.spendingPublicKey <== spendingPublicKey;
  sigVerifier.eddsaSignature <== eddsaSignature;
  sigVerifier.signedMessageHash <== signedMessageHash;
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L120-151)
```text
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
