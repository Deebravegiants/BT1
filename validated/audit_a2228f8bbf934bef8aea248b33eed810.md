### Title
Nullifier binds only to `(commitment, nullifyingPrivateKey)`, not leaf position — duplicate-value outputs to the same stealth address permanently freeze one UTXO - (File: `circuits/OriginalCommitmentCalculator.circom`, `circuits/NullifierCalculator.circom`, `circuits/MainEVMCircuit.circom`)

### Summary
The output commitment hash `Poseidon(amount, erc20TokenAddress, publicKey, timeStamp)` [1](#0-0)  has no per-output blinding/randomizer beyond `timeStamp`, and `timeStamp` is a single value shared by *every* output in a transaction (`signal input outTimeStamp;`) [2](#0-1) . When it is later spent, the nullifier is derived purely from `(commitment, signature=Poseidon(nullifyingPrivateKey, commitment))` [3](#0-2) [4](#0-3)  — it never binds to the leaf's tree position. This is the same class of bug as the report's "constant/insufficiently-unique nonce": a value meant to guarantee uniqueness of a cryptographic artifact is not actually forced to be unique, so two distinct, independently valid leaves can collapse to one identifier.

### Finding Description
An unprivileged sender fully controls, in a single `transact()` call, the per-token `outAmounts[i][j]`, `outPublicKeys[i][j]` and the shared `outTimeStamp` for all outputs of that transaction [5](#0-4) . If two output slots use the same `amount`, the same `erc20TokenAddresses[i]`, and the same recipient `publicKey` (i.e., sender sends the recipient two equal-value notes in one transaction, or the sender reuses the same ephemeral stealth key for two outputs), `OriginalCommitmentCalculator` produces the identical `commitment` value for both [6](#0-5) . Both commitments are inserted as distinct leaves at different tree indices via `insertCommitments`, with no dedup check [7](#0-6) , and both are counted toward the balance equation as legitimate value [8](#0-7) .

When the recipient later spends one of these UTXOs, `NullifierCalculator` computes `nullifier = Poseidon(commitment, signature)` where `signature = Poseidon(nullifyingPrivateKey, commitment)` — both inputs are identical for the duplicate leaf [3](#0-2) [4](#0-3) . `HinkalBase.insertNullifiers` records the nullifier globally and rejects any future transaction reusing it: `require(!nullifiers[inputNullifiers[i][j]], "Nullifier cannot be reused")` [9](#0-8) . Consequently, once the first of the two duplicate-value UTXOs is spent, the second — a distinct, unspent leaf with its own valid Merkle inclusion proof — can never be nullified: any attempt to spend it produces the exact same nullifier, which is already marked used. The equality broken is: *every value-bearing leaf the tree accepts must remain independently spendable via a unique nullifier*; here two independently-created, independently-valid leaves share one nullifier, so one becomes permanently unspendable even though its value was accepted into the balance accounting when created.

### Impact Explanation
This is a permanent freezing of user funds triggered without any privileged access: a normal sender constructing an ordinary `transact()` call can create two duplicate-value notes to the same recipient stealth address in one transaction, and the recipient will permanently lose access to one of them once they spend the other. This matches the in-scope "High" impact category (permanent freezing of user funds) since the loss falls on the recipient, not the crafting sender's own balance.

### Likelihood Explanation
No special privileges, oracle assumptions, or admin/relay roles are needed. The attacker only needs to control `outAmounts`, `outPublicKeys`, and the shared `outTimeStamp` for a normal transaction to the target recipient — all standard, prover-supplied fields already exercised on every legitimate transact call. The main practical constraint is that the attacker (sender) must choose an `outPublicKeys[i][j]` value that matches the recipient's expected stealth-address derivation for two separate outputs with the same amount, which is achievable by reusing the same ephemeral key material for both outputs when constructing the payment — no cryptographic break is required, only failure to vary the shared `timeStamp`/output tuple.

### Recommendation
Bind the nullifier (or the commitment) to something that is guaranteed unique per leaf — e.g., include the actual Merkle leaf index/position, or a distinct per-output randomizer/blinding factor supplied per output rather than one `outTimeStamp` shared across the whole transaction — in the Poseidon preimage used for `NullifierCalculator`/`OriginalCommitmentCalculator`. Short term, make `timeStamp` (or an explicit per-output nonce) unique per output signal instead of a single transaction-wide value, and add a circuit constraint forcing distinctness of `(amount, erc20TokenAddress, publicKey, timeStamp)` tuples within one transaction's outputs.

### Proof of Concept
1. Sender calls `transact()` with `tokenCount=1`, `outputCount=2`, setting `outAmounts[0][0] = outAmounts[0][1] = X`, `outPublicKeys[0][0] = outPublicKeys[0][1] = P` (recipient's stealth public key derived with the same ephemeral value for both outputs), and the single `outTimeStamp` shared by both.
2. `OriginalCommitmentCalculator` yields `commitment0 = commitment1 = Poseidon(X, token, P, outTimeStamp)` for both outputs; both pass `calcOutCommitment[i][j].out === outCommitments[i][j]` [10](#0-9) , and both are inserted into the Merkle tree as separate leaves via `insertCommitments` [11](#0-10) .
3. Recipient spends the first UTXO: proof computes `signature = Poseidon(nullifyingPrivateKey, commitment0)`, `nullifier = Poseidon(commitment0, signature)`; `insertNullifiers` marks this nullifier as used [9](#0-8) .
4. Recipient attempts to spend the second (still-unspent, independently valid) leaf: the circuit computes the identical `commitment1`/`signature`/`nullifier` as in step 3, and `transact()` reverts with `"Nullifier cannot be reused"`, permanently freezing that UTXO's value.

### Citations

**File:** circuits/OriginalCommitmentCalculator.circom (L6-22)
```text
template OriginalCommitmentCalculator() {
  signal input amount;
  signal input erc20TokenAddress;
  signal input publicKey;
  signal input timeStamp;
  signal output out;

  component calcIsAmountZero = IsZero();
  calcIsAmountZero.in <== amount;

  component calcCommitment = Poseidon(4);
  calcCommitment.inputs[0] <== amount;
  calcCommitment.inputs[1] <== erc20TokenAddress;
  calcCommitment.inputs[2] <== publicKey;
  calcCommitment.inputs[3] <== timeStamp;

  out <== calcCommitment.out * (1 - calcIsAmountZero.out);
```

**File:** circuits/MainEVMCircuit.circom (L47-50)
```text
  signal input outAmounts[tokenCount][outputCount];
  signal input outTimeStamp;
  signal input outPublicKeys[tokenCount][outputCount];
  signal input outCommitments[tokenCount][outputCount];
```

**File:** circuits/MainEVMCircuit.circom (L152-165)
```text
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
```

**File:** circuits/Signature.circom (L10-13)
```text
    component hasher = Poseidon(2);
    hasher.inputs[0] <== nullifyingPrivateKey;
    hasher.inputs[1] <== commitment;
    out <== hasher.out;
```

**File:** circuits/NullifierCalculator.circom (L11-18)
```text
  component calcOriginalNullifier = Poseidon(2);
  calcOriginalNullifier.inputs[0] <== commitment;
  calcOriginalNullifier.inputs[1] <== signature;

  component calcCommitmentIsZero = IsZero();
  calcCommitmentIsZero.in <== commitment;

  out <== calcOriginalNullifier.out * (1 - calcCommitmentIsZero.out);
```

**File:** contracts/HinkalBase.sol (L72-133)
```text
    function insertCommitments(
        uint256[][] memory offChainCommitments,
        bytes[][] memory offChainEncryptedOutputs,
        OnChainCommitment[] memory onChainCommitments,
        bool[] memory onChainCreation
    ) internal {
        // 1) Total Length of Commitments
        uint256 length = 0;
        for (uint256 i = 0; i < offChainCommitments.length; i++) {
            for (uint256 j = 0; j < offChainCommitments[i].length; j++) {
                if (onChainCreation[i]) break;
                length += offChainCommitments[i][j] != 0 ? 1 : 0;
            }
        }
        length += onChainCommitments.length;

        if (length > 0) {
            // 2) Flattening leaves array
            uint256[] memory leaves = new uint256[](length);
            uint256 index = 0;
            for (uint256 i = 0; i < offChainCommitments.length; i++) {
                for (uint256 j = 0; j < offChainCommitments[i].length; j++) {
                    if (onChainCreation[i] == true) break;
                    if (offChainCommitments[i][j] != 0) {
                        leaves[index++] = offChainCommitments[i][j];
                    }
                }
            }
            for (uint256 i = 0; i < onChainCommitments.length; i++) {
                leaves[index++] = onChainCommitments[i].commitment;
            }

            // 3) Inserting Leaves
            uint256[] memory insertedIndexes = insertMany(leaves);

            // 4) Emitting Commitments/EncryptedOutputs
            index = 0;
            for (uint256 i = 0; i < offChainEncryptedOutputs.length; i++) {
                for (uint256 j = 0; j < offChainEncryptedOutputs[i].length; j++) {
                    if (onChainCreation[i] == true) break;
                    if (offChainCommitments[i][j] != 0) {
                        emit NewCommitment(
                            leaves[index],
                            int256(insertedIndexes[index]),
                            offChainEncryptedOutputs[i][j]
                        );
                        index++;
                    }
                }
            }
            for (uint256 i = 0; i < onChainCommitments.length; i++) {
                emit NewCommitment(
                    leaves[index],
                    -1 * int256(insertedIndexes[index++]),
                    abi.encode(
                        onChainCommitments[i].utxo,
                        onChainCommitments[i].onChainEncryptedOutput
                    )
                );
            }
        }
    }
```

**File:** contracts/HinkalBase.sol (L135-150)
```text
    function insertNullifiers(
        uint256[][] calldata inputNullifiers,
        bool[] calldata onChainCreation
    ) internal {
        for (uint256 i = 0; i < inputNullifiers.length; i++) {
            for (uint256 j = 0; j < inputNullifiers[i].length; j++) {
                if (onChainCreation[i] == true) break;
                if (inputNullifiers[i][j] != 0) {
                    require(
                        !nullifiers[inputNullifiers[i][j]],
                        "Nullifier cannot be reused"
                    );
                    nullifiers[inputNullifiers[i][j]] = true;
                    emit Nullified(inputNullifiers[i][j]);
                }
            }
```

**File:** contracts/Hinkal.sol (L116-132)
```text
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
```
