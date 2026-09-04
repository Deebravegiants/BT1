### Title
Global `usedMessages` nonce namespace lets an attacker front-run and permanently invalidate a victim's signed Emporium message — ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`verifyWallet` marks `usedMessages[circomData.emporiumMessage] = true` unconditionally before checking `stack.signerAddress`, and the `emporiumMessage` namespace is global rather than scoped to a specific signer. Because `emporiumMessage` is a fully attacker-chosen public input with no circuit or contract binding to a particular signer's identity, an unprivileged attacker can submit their own unrelated, stateless (`signerAddress == address(0)`) `transact` call using the exact `emporiumMessage` value a victim intends to use for a signed, stateful (Case 1) operation, permanently consuming that nonce before the victim's legitimately signed message can land.

### Finding Description
The claimed equality is: *one `emporiumMessage` nonce == one legitimately-authorized execution intended by the party who chose it*. This equality is broken because the nonce space is not bound to any signer.

In `verifyWallet`: [1](#0-0) 
the check-and-set of `$.usedMessages[circomData.emporiumMessage]` happens before any signature validation, and if `stack.signerAddress == address(0)` the function returns immediately without checking any signature at all — this is the intended "stateless"/relay-paid path used for Case 2 operations in `runAction`: [2](#0-1) 

`circomData.emporiumMessage` is attacker-supplied calldata for their *own* proof/transaction — it is embedded as a plain public input value in `formBasicInput`/`getSignedMessageHash` (or `formInputEmporiumMin`) with no constraint tying it to the caller's spending key, nullifiers, or any specific signer: [3](#0-2) [4](#0-3) 
An attacker who observes (e.g., in a relay/mempool) a victim's chosen `emporiumMessage = M` (created for the victim's EIP-712-signed `EmporiumSignature`) can generate their own valid ZK proof (spending their own UTXOs, signed with their own EdDSA key over a `signedMessageHash` that merely *incorporates* `M` as one of many hashed inputs) with `circomData.emporiumMessage = M` and `stack.signerAddress = address(0)`. This transaction passes normal proof/nullifier checks (it's a fully valid, self-consistent proof for the attacker's own funds) and reaches `verifyWallet`, which sets `usedMessages[M] = true` and returns early, without ever checking a signature bound to the victim.

When the victim later submits their own correctly signed stack with `emporiumMessage = M` and `stack.signerAddress != address(0)`, `verifyWallet` reverts at line 308-310 with `UsedMessage()` before signature verification is even reached, permanently blocking that message.

No existing guard prevents this: `performHinkalChecks`, `verifyProof`, `rootHashExists`, `insertNullifiers`, and `onlyAllowedRecipient` all validate the *attacker's own* proof/action correctly — none of them scope or bind `emporiumMessage` to a specific signer/spender identity, and `verifyWallet` itself performs the state-changing write (`usedMessages[...] = true`) before the signer-specific signature check that would otherwise gate it.

### Impact Explanation
The victim's specific, already-signed queued Emporium operation (their `EmporiumSignature` for ops/maxFee/deadline tied to `M`) becomes permanently unusable — no other value of `emporiumMessage` will satisfy the signature they already produced for `M`, so the specific authorized call sequence they signed can never execute. This is a griefing/freezing primitive targeting a specific victim's stateful operation set. It affects only the party whose nonce is targeted (repeatable against any victim whose `emporiumMessage` is observable off-chain before landing on-chain), and the attacker's cost is just gas for a normal, valid, otherwise legitimate self-funded stateless Emporium transaction.

### Likelihood Explanation
Preconditions: the attacker must learn the victim's `emporiumMessage` value before the victim's transaction is mined (e.g., via a public relay queue, shared coordinator, or mempool visibility) — the same precondition assumed by the question's own proof idea ("front-runs"). Attacker cost is one ordinary self-funded `transact` call; no privileged role or victim key material is required. This is straightforward to execute deterministically given mempool/relay visibility of the target nonce.

### Recommendation
Scope the `usedMessages` mapping (or the equivalent invalidation key) to the intended signer, e.g. `usedMessages[keccak256(abi.encode(signerAddress, emporiumMessage))]`, or require that the stateless path (`signerAddress == address(0)`) use a disjoint nonce space from the signed/stateful path so that an unrelated stateless call cannot consume a nonce meant for a specific signer's EIP-712 message. Alternatively, defer the `usedMessages[...] = true` write until after the signature (or explicit "no signer required") branch has been fully validated for the specific message/signer pairing.

### Proof of Concept
Foundry test outline:
1. Deploy `EmporiumUpgradeable` and required Hinkal infra (proof verifier mock accepting any valid-structured proof, or use the real verifier with locally generated proofs).
2. Victim: off-chain, compute `emporiumMessage = M`, build `EmporiumOperation[] ops`, `maxFee`, `deadline`, and sign the `EMPORIUM_SIGNATURE_TYPEHASH` struct with victim's private key producing `(v, r, s)`; assemble `EmporiumStack{signerAddress: victim, v, r, s, ops, maxFee, deadline}` and a valid `CircomData` with `emporiumMessage = M` and a valid proof spending the victim's own UTXOs for Case 1.
3. Attacker: build their own valid `CircomData`/proof (own UTXOs, own action), but set `circomData.emporiumMessage = M` and `EmporiumStack{signerAddress: address(0), ...}` (Case 2, stateless), and submit `transact` first.
4. Assert attacker's transaction succeeds and `usedMessages[M] == true` afterward (read via a harness that exposes `_getEmporiumStorage()` or by observing the revert behavior).
5. Victim then submits their properly signed `transact` call with `emporiumMessage = M`; assert it reverts with `EmporiumUpgradeable.UsedMessage()`, proving the victim's authorized operation can never execute under this `M`.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L91-113)
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

**File:** contracts/CircomDataBuilder.sol (L150-201)
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

    function formInputNormal(
        uint256 chainId,
        address verifyingContract,
        CircomData calldata circomData
    ) internal pure returns (uint256[] memory input) {
        input = new uint256[](circomData.publicSignalCount);
        uint16 index = 0;
        input = formBasicInput(
            chainId,
            verifyingContract,
            circomData,
            input,
            index,
            circomData.emporiumMessage
        );
    }

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
