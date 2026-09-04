### Title
`calldataHash` public signal is declared but never constrained in `MainEVMCircuit`/`MainEVMCircuitMin`, allowing proof reuse against arbitrary `CircomData` - (File: `circuits/MainEVMCircuit.circom`, `circuits/MainEVMCircuitMin.circom`)

### Summary
`calldataHash` is meant to cryptographically bind a ZK proof to the exact off-chain-agreed `CircomData` (external action, fee structure, hook data, slippage values, on-chain-creation flags, `originalSender`, `extraData`, encrypted outputs, etc.), analogous to how the Swivel bug involved a field (`underlying`) that was assumed to resolve correctly but actually never behaved as intended. In this repo, `calldataHash` is declared as a `signal input` in both `circuits/MainEVMCircuit.circom` and `circuits/MainEVMCircuitMin.circom`, but it is never used in any constraint (`===`, or passed into any sub-component whose output is constrained) anywhere in the circuit body.

### Finding Description
`contracts/HinkalHelper.sol::performHinkalChecks` requires `CircomDataBuilder.getHashedCalldata(circomData) == circomData.calldataHash` [1](#0-0)  and then builds the public input array via `CircomDataBuilder.formInputForCircom`/`formBasicInput`, which places `circomData.calldataHash` into the public input vector passed to the Groth16/Plonk verifier [2](#0-1) . `getHashedCalldata` folds in `externalActionData`, `feeStructure`, `hookData`, `slippageValues`, `onChainCreation`, `originalSender`, `extraData`, and `encryptedOutputs` [3](#0-2) .

The intent is clearly that this hash acts as a tamper-proof binding: the prover commits to these values at proof-generation time via the `calldataHash` public signal, so that a relay or attacker cannot swap in a different `externalActionData.externalAddress`, `feeStructure`, `hookData`, or `originalSender` after the proof is generated.

However, inside `circuits/MainEVMCircuit.circom`, `signal input calldataHash;` is declared on line 52 but is never referenced again in the entire template body — it is not passed to any component, not compared with `===`, and does not feed into `message <== Poseidon(1)([messageSeed])` or any other constraint [4](#0-3) . All constraints in the circuit (nullifier checks, merkle root checks, in/out amount balance, distinct-address checks) operate on `rootHashHinkal`, `signedMessageHash`, `erc20TokenAddresses`, `amountChanges`, `inNullifiers`, `outCommitments`, `inAmounts`/`outAmounts`, none of which involve `calldataHash` [5](#0-4) . The same pattern exists in `circuits/MainEVMCircuitMin.circom`, where `calldataHash` is declared as a public input (line 9) but the circuit body only computes `message <== Poseidon(1)([messageSeed])`, again never touching `calldataHash` [6](#0-5) .

Because `calldataHash` does not appear in any R1CS constraint, a Groth16 (or Plonk) proof generated with one value of `calldataHash` remains valid when verified with a completely different value substituted into that public-input slot — R1CS/QAP satisfaction is unaffected by public signals that never enter any constraint. This breaks the equality the protocol relies on: "the SNARK proof authorizes exactly this `circomData`" is supposed to be enforced through `calldataHash` being a constrained public input, but it is not enforced by the circuit at all — only by the (bypassable) Solidity-side re-derivation check, which itself doesn't stop reuse of the *same* proof `(a,b,c)` against a *different* `calldataHash` value/`CircomData` payload, since the on-chain check only verifies that the caller-supplied `circomData.calldataHash` matches a hash of the caller-supplied `circomData` — not that the proof was generated for that specific hash.

### Impact Explanation
This is a proof-verification bypass on a field that is meant to authorize the entire non-monetary transaction metadata (external action target/address, hook contracts and their metadata, fee structure, slippage, `originalSender`). A malicious relay or the depositor's counterparty could take a validly-produced proof for one set of `externalActionData`/`hookData`/`feeStructure`/`originalSender`, then submit the transaction with a *different* `circomData` (recomputing a fresh, matching `calldataHash` and passing the Solidity-side hash-integrity check), while reusing the same `(a,b,c)` proof and the same `inputForCircom` values for the *other* public signals (`rootHashHinkal`, `signedMessageHash`, token addresses, amounts, nullifiers, commitments) that remain unchanged. Since the proof never actually constrained `calldataHash`, verification still succeeds. This lets an attacker redirect calls to a `postHookContract`/`preHookContract`, external action address, relay, or fee parameters the original prover/signer never authorized — i.e., "executing calls or moving assets a wallet owner or prover never authorised," which fits the in-scope High-impact category (and, depending on what is substituted — e.g., a self-controlled `relay`/`externalActionData.externalAddress` diverting the funds moved by the deltaAmount transfers in `Hinkal.sol`/`ExternalActionBase*` — could rise to fund theft, a Critical impact).

### Likelihood Explanation
The gap is a fundamental, always-present property of the deployed circuit (not a rare edge case): every proof generated for `MainEVMCircuit`/`MainEVMCircuitMin` has this unconstrained public signal, so any relay or any party with visibility into a signed proof/transaction (e.g., through the mempool, or a colluding/malicious relay handling `circomData.relay`) can attempt this substitution. Exploitation requires only recomputing `calldataHash` for the substituted `CircomData` in the same call (trivial, since `getHashedCalldata` is a pure keccak function) and reusing the untouched public inputs and proof bytes.

### Recommendation
Add an explicit constraint tying `calldataHash` to the actual circuit computation, e.g. `calldataHash === <a Poseidon/hash of all bound fields, or at minimum an equality/inclusion constraint that forces the verifier to reject any value not fixed at proof-generation time>`. At minimum, wire `calldataHash` into an existing constrained signal (e.g., include it inside the `message`/`messageSeed` hashing, or force `calldataHash === somePoseidonHash` derived from private witness data) so that changing its public value invalidates the proof. Apply the same fix to `MainEVMCircuitMin.circom`.

### Proof of Concept
1. Generate a normal, valid proof for a transaction with `circomData_A` containing `externalActionData.externalAddress = SwapAction`, `hookData = {}`, `feeStructure = {feeToken: USDC, ...}`, computing `calldataHash_A = CircomDataBuilder.getHashedCalldata(circomData_A)` per `contracts/CircomDataBuilder.sol` lines 10-18, and forming `inputForCircom` per `formBasicInput` (lines 180-240).
2. Craft `circomData_B` that is identical in every field that maps into `inputForCircom` besides `calldataHash` (i.e., same `rootHashHinkal`, `erc20TokenAddresses`, `amountChanges`, `inputNullifiers`, `outCommitments`, `timeStamp`, `stealthAddressStructure`), but with a different `externalActionData.externalAddress` (e.g., pointing to a malicious `IExternalActionV2` contract), different `feeStructure` (e.g., diverting the relay fee), or different `hookData.postHookContract`.
3. Compute `calldataHash_B = CircomDataBuilder.getHashedCalldata(circomData_B)`.
4. Call `Hinkal.transact(a, b, c, dimensions, circomData_B)` reusing the same proof `(a, b, c)` originally generated for `circomData_A`. Because `formInputForCircom`/`formBasicInput` places `calldataHash_B` (matching `circomData_B.calldataHash`, satisfying the Solidity-side hash check in `HinkalHelper.performHinkalChecks` lines 221-225) into the public input array, and because the circuit (`MainEVMCircuit.circom`) never constrains `calldataHash` to anything, `verifyProof` still succeeds despite the proof having been produced for a completely different external action / hook / fee target.

### Citations

**File:** contracts/HinkalHelper.sol (L221-225)
```text
        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
        );
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

**File:** circuits/MainEVMCircuit.circom (L52-62)
```text
  signal input calldataHash;

  signal input messageSeed;

  signal input H0Ax; // for creating a stealth address
  signal input H0Ay; // for creating a stealth address
  signal output outH1Ax;
  signal output outH1Ay;
  signal output outStealthAddress;

  signal output message;
```

**File:** circuits/MainEVMCircuit.circom (L100-182)
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

  component distinctErc20AddressChecks[tokenCount * (tokenCount-1)/2];
  var index = 0;
  for (var i =0; i< tokenCount-1;i++){
    for (var j = i+1; j< tokenCount; j++)
    {
      distinctErc20AddressChecks[index] = IsEqual();
      distinctErc20AddressChecks[index].in[0] <== erc20TokenAddresses[i];
      distinctErc20AddressChecks[index].in[1] <== erc20TokenAddresses[j];
      distinctErc20AddressChecks[index].out === 0;
      index++;
    }
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
