### Title
Unconstrained `calldataHash` public signal in `MainEVMCircuit` allows swapping external-action/hook/fee metadata without prover authorisation - ([File: circuits/MainEVMCircuit.circom])

### Summary
`circomData.calldataHash` is meant to cryptographically bind the metadata fields of a transaction (`externalActionData`, `hookData`, `feeStructure`, `slippageValues`, `relay`, `onChainCreation`, `originalSender`, `extraData`, `publicSignalCount`) to the zk-SNARK proof that authorises a `transact()` call, exactly the way `signedMessageHash` binds the token/amount/nullifier/commitment fields. On-chain, `HinkalHelper.performHinkalChecks` recomputes this hash from the submitted `CircomData` and requires it to equal `circomData.calldataHash` [1](#0-0) , and the same value is also placed into the public-input array fed to the Groth16 verifier [2](#0-1) . However, inside `MainEVMCircuit.circom` the `calldataHash` signal is declared as an input but never appears in any constraint (`<==`, `===`, or as an argument to any sub-component) [3](#0-2) . Because it is a fully unconstrained public signal in the R1CS, a Groth16 proof generated once by the original prover remains valid for *any* value plugged into that public-input slot at verification time — the pairing check does not actually tie the proof to a specific `calldataHash`.

### Finding Description
`MainEVMCircuit` publicly declares `rootHashHinkal, signedMessageHash, erc20TokenAddresses, amountChanges, outTimeStamp, inNullifiers, outCommitments, calldataHash, message, ...` as its public inputs [4](#0-3) . Every other public signal in this list is actually consumed by a constraint: `signedMessageHash` feeds the EdDSA `SignatureVerifier` [5](#0-4) , `rootHashHinkal` is force-equal-checked against the recomputed Merkle root [6](#0-5) , `outCommitments`/`inNullifiers`/`erc20TokenAddresses`/`amountChanges` all drive the commitment/nullifier/balance equalities [7](#0-6) . `calldataHash`, by contrast, is declared and never touched again anywhere in the file.

Because Groth16 soundness for a given public input index depends on that signal actually appearing in the constraint system's selector polynomials, a signal that is never referenced by any constraint is a "free" wire: the value supplied to the verifier for that index does not have to match anything the prover computed during witness generation for the proof to still satisfy the pairing equation. Concretely, this means: take a validly generated proof `(a,b,c)` for some legitimate `CircomData` (call it `CD1`), whose `calldataHash1 = getHashedCalldata(CD1)`. An attacker (anyone submitting/relaying the transaction, since `transact()` is a public, permissionless entrypoint) can construct a different `CircomData` `CD2` that changes only the fields covered by `getHashedCalldata`/`getHashedCalldata1`/`getHashedCalldata2` — i.e. `relay`, `externalActionData`, `slippageValues`, `hookData`, `encryptedOutputs`, `onChainEncryptedOutput`, `feeStructure`, `onChainCreation`, `originalSender`, `extraData`, `publicSignalCount` [8](#0-7)  — compute `calldataHash2 = getHashedCalldata(CD2)`, and submit the *same* proof `(a,b,c)` together with `CD2` and `calldataHash2` in place of `calldataHash1`. The on-chain check in `performHinkalChecks` will pass (it only checks internal self-consistency of `CD2`, not that the proof was generated for it) [1](#0-0) , and `verifyProof` will also pass because the circuit places no constraint tying `a,b,c` to that specific public-input slot value.

The remaining transaction-critical fields — token addresses, amounts, nullifiers, output commitments, root hash, stealth address — are protected because they are covered by `signedMessageHash`, which *is* constrained via the EdDSA signature check, and/or are directly wired into circuit equalities. So the shielded balance/nullifier/commitment invariants themselves are not directly forgeable this way. But the metadata fields hashed only into `calldataHash` are exactly the fields that control **what code executes and where value flows during external actions and hooks**: `externalActionData.externalAddress`/`externalActionId`/`externalActionMetadata` (which external-action contract is invoked and with what parameters), `hookData.preHookContract`/`postHookContract` (arbitrary pre/post-transact hook contracts to run), `feeStructure` (fee token/rate charged), `slippageValues` (the user's minimum-received protection), and `onChainCreation`/`originalSender`/`extraData`.

### Impact Explanation
Because `calldataHash` is not actually bound by the proof, a party resubmitting (front-running, or simply re-broadcasting/relaying) a captured valid proof can rewrite: which `externalActionData.externalAddress` is invoked (an attacker-controlled malicious "external action" contract instead of the legitimate swap/on-chain-deposit action, which under `Hinkal.sol`'s `_externalTransact` flow can move ERC20/ETH balances tracked via `getBalancesForArray`/`utxoSet` [9](#0-8) ), which `hookData.preHookContract`/`postHookContract` get executed against the transaction (arbitrary contract call authorised implicitly by the (now-decoupled) proof), the `feeStructure` (fee token/rate diverted to a different recipient), and the `slippageValues` (dropping the user's minimum-received protection to `0` or negative, allowing a worse trade to pass the `balanceDif >= circomData.slippageValues[i]` check [10](#0-9) ). This is an unauthorised wallet/contract-call redirection and fee/slippage manipulation that the original prover/signer never approved — a "wallet op not authorised by the prover or signer," qualifying at minimum as High impact (theft/freezing of protocol or relay fees, or forced execution of unauthorised external calls/hooks), and potentially Critical if the redirected external action or hook is used to drain the ERC20 allowance or output UTXOs generated by the same transaction.

### Likelihood Explanation
Any transaction submitted to `transact()` is public calldata (mempool-visible before inclusion, or trivially re-extractable from a mined transaction), and `transact()` has no access control tying the caller to the original prover — anyone can call it with a valid `(a,b,c)` proof and self-consistent `CircomData`. The only work needed by an attacker is recomputing `getHashedCalldata` for the modified metadata fields (a pure, publicly computable keccak256 function) [11](#0-10) , which requires no cryptographic secret. This makes the likelihood high whenever externalActionData/hookData is economically meaningful (e.g., an emporium withdraw/swap that a bot or the intended relay itself submits) and a competing party is watching the mempool or intercepts the relay flow.

### Recommendation
Add an explicit constraint in `MainEVMCircuit.circom` (and any other circuit using `calldataHash`, e.g. `MainEVMCircuitMin.circom`) that ties `calldataHash` into the witness, e.g. via a dummy multiplication/assert (`calldataHash * 1 === calldataHash;` is insufficient — it must be forced through an actual constraint that references the signal, such as folding it into the `message`/nullifier/signature Poseidon hash chain, or explicitly asserting `calldataHash === somePrivateWitnessOfCalldataHash` that is derived from data the prover commits to). At minimum, incorporate `calldataHash` as an input to the existing `Poseidon(1)([messageSeed])` message construction or into the `SignatureVerifier`'s signed payload, so that the EdDSA signature (already correctly bound via `signedMessageHash`) transitively also commits to `calldataHash`, restoring the intended non-malleability of the metadata fields.

### Proof of Concept
1. User/relay generates a valid Groth16 proof `(a,b,c)` for `CircomData CD1` where `CD1.calldataHash = getHashedCalldata(CD1)`, with `CD1.externalActionData` pointing to the legitimate swap external action and `CD1.slippageValues[i] = minAcceptable`.
2. Attacker observes this pending transaction (mempool or already-broadcast) and constructs `CD2`, identical to `CD1` in every field that feeds `signedMessageHash`/the circuit's constrained public inputs (`rootHashHinkal`, `erc20TokenAddresses`, `amountChanges`, `timeStamp`, `inputNullifiers`, `outCommitments`, `stealthAddressStructure`), but with `CD2.externalActionData.externalAddress` = attacker-controlled contract and/or `CD2.slippageValues[i] = 0` and/or `CD2.hookData.postHookContract` = attacker contract.
3. Attacker computes `calldataHash2 = getHashedCalldata(CD2)` off-chain (pure function, no secret needed) and sets `CD2.calldataHash = calldataHash2`.
4. Attacker calls `Hinkal.transact(a, b, c, dimensions, CD2)` directly, front-running/replacing the original submission.
5. `performHinkalChecks` succeeds (self-consistent hash check on `CD2`) [1](#0-0) ; `verifyProof(a,b,c,inputForCircom,...)` succeeds because `calldataHash` never appears in any circuit constraint, so any value in that public-input slot is accepted alongside the original `(a,b,c)`.
6. `_externalTransact`/hooks now execute with the attacker's substituted `externalActionData`/`hookData`/`feeStructure`/`slippageValues`, none of which the original signer/prover authorised.

Note: I was not able to execute this end-to-end against a live circuit/verifier build (no test/compilation tooling available in this environment) to empirically confirm the Groth16 "unconstrained public input" behavior for this specific compiled circuit; the finding is based on static analysis of the `.circom` source showing `calldataHash` has zero constraints, which is a well-documented Circom/Groth16 soundness pitfall for unused public signals.

### Citations

**File:** contracts/HinkalHelper.sol (L221-225)
```text
        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
        );
```

**File:** contracts/CircomDataBuilder.sol (L10-18)
```text
    function getHashedCalldata(
        CircomData calldata circomData
    ) internal pure returns (uint256) {
        // because of stack too deep error, we need to split the calldata into two parts
        uint256 calldataHash1 = getHashedCalldata1(circomData);
        uint256 calldataHash2 = getHashedCalldata2(circomData);
        return (uint256(keccak256(abi.encode(calldataHash1, calldataHash2))) %
            CIRCOM_P);
    }
```

**File:** contracts/CircomDataBuilder.sol (L20-54)
```text
    function getHashedCalldata1(
        CircomData calldata circomData
    ) internal pure returns (uint256) {
        return
            uint256(
                keccak256(
                    abi.encode(
                        circomData.publicSignalCount,
                        circomData.relay,
                        circomData.emporiumMessage,
                        circomData.externalActionData,
                        circomData.slippageValues
                    )
                )
            );
    }

    function getHashedCalldata2(
        CircomData calldata circomData
    ) internal pure returns (uint256) {
        return
            uint256(
                keccak256(
                    abi.encode(
                        circomData.hookData,
                        circomData.encryptedOutputs,
                        circomData.onChainEncryptedOutput,
                        circomData.feeStructure,
                        circomData.onChainCreation,
                        circomData.originalSender,
                        circomData.extraData
                    )
                )
            );
    }
```

**File:** contracts/CircomDataBuilder.sol (L234-234)
```text
        input[index++] = circomData.calldataHash;
```

**File:** circuits/MainEVMCircuit.circom (L17-21)
```text
// public params: 
// rootHashHinkal, signedMessageHash, 
// erc20TokenAddresses, amountChanges, outTimeStamp, inNullifiers, outCommitments, 
// calldataHash, message,
// outH1Ax, outH1Ay, H0Ax, H0Ay, outStealthAddress
```

**File:** circuits/MainEVMCircuit.circom (L52-52)
```text
  signal input calldataHash;
```

**File:** circuits/MainEVMCircuit.circom (L91-95)
```text
  // verifying signature
  component sigVerifier = SignatureVerifier();
  sigVerifier.spendingPublicKey <== spendingPublicKey;
  sigVerifier.eddsaSignature <== eddsaSignature;
  sigVerifier.signedMessageHash <== signedMessageHash;
```

**File:** circuits/MainEVMCircuit.circom (L144-148)
```text
        // 5) Checking that transaction root hash is legit
        calcEqual[i][j] = ForceEqualIfEnabled();
        calcEqual[i][j].in[0] <== calcTransactionRootHash[i][j].rootHash;
        calcEqual[i][j].in[1] <== rootHashHinkal;
        calcEqual[i][j].enabled <== inAmounts[i][j];
```

**File:** circuits/MainEVMCircuit.circom (L160-168)
```text
      calcOutCommitment[i][j].out === outCommitments[i][j];

      preventOutOverflow[i][j] = OverflowPreventer(outputCount);
      preventOutOverflow[i][j].in <== outAmounts[i][j];
      outTotal += outAmounts[i][j];
    }

      // for each token type, the sum of refund and swapped amount should be equal to the sum of input amounts
      inTotal + amountChanges[i] === outTotal;
```

**File:** contracts/Hinkal.sol (L82-120)
```text
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
```
