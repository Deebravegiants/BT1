### Title
Missing per-output entropy in commitment preimage lets duplicate (amount, token, stealth, timeStamp) UTXOs collide on nullifier, permanently stranding backed value - (File: circuits/OriginalCommitmentCalculator.circom / circuits/NullifierCalculator.circom)

### Summary
The commitment preimage `Poseidon(amount, erc20TokenAddress, publicKey, timeStamp)` and the nullifier `Poseidon(commitment, Poseidon(nullifyingPrivateKey, commitment))` contain no per-UTXO nonce or leaf-index binding. Because `outTimeStamp` is a single signal shared by every output within one `MainEVMCircuit` invocation, any user can trivially produce two outputs in the same `transact` call with identical `(amount, token, publicKey, timeStamp)`, yielding two tree leaves with the identical commitment and, later, the identical nullifier.

### Finding Description
The claimed equality that should hold is: **one value-bearing leaf ↔ one nullifier that can ever be recorded for it**. This breaks because the nullifier value is a pure function of `(commitment, nullifyingPrivateKey)` with no dependency on the leaf's tree index or any per-output randomness: [1](#0-0) [2](#0-1) [3](#0-2) 

In `MainEVMCircuit.circom`, `outTimeStamp` is declared once (not per-output) and reused for every `outAmounts[i][j]`/`outPublicKeys[i][j]` pair when computing `calcOutCommitment[i][j].out`: [4](#0-3) [5](#0-4) 

An attacker (any depositor, spending only their own funds) can therefore craft `outAmounts[i][j1] == outAmounts[i][j2]` with `outPublicKeys[i][j1] == outPublicKeys[i][j2]` for the same token `i` in a single `transact` call. Both resulting `outCommitments` are numerically identical Poseidon hashes, so `insertCommitments` inserts the same leaf value at two different tree positions (`HinkalBase.insertCommitments`). Nothing in `Hinkal.sol`/`HinkalHelper.sol` checks `outCommitments` for uniqueness (`dimensionsCheck`, `checkOnchainCreation`, and `performHinkalChecks` only validate calldata-hash integrity, relay legitimacy, and onChainCreation constraints, not leaf distinctness): [6](#0-5) 

When the owner of that stealth key later spends **either** leaf, the circuit recomputes `commitment` from the same `(amount, token, publicKey, timeStamp)` and the same `signature = Poseidon(nullifyingPrivateKey, commitment)`, producing the same `nullifier` regardless of which Merkle path (siblings/sides) was used to prove inclusion. `HinkalBase.insertNullifiers` marks that nullifier as spent: [7](#0-6) 

Any later attempt to spend the second, structurally-distinct leaf (different tree index, same value) recomputes the identical nullifier and reverts with `"Nullifier cannot be reused"`. Because `insertNullifiers` reverts the whole transaction atomically, that second leaf's value can never be extracted by any subsequent proof - it is not a double-spend in the "steal twice" direction, but a permanent inability to ever record a valid spend for a leaf that is fully backed by real, previously-verified balance (`balanceDif == amountChanges[i] + utxoAmount` was already enforced at creation time in `Hinkal.sol`).

Existing guards do not catch this:
- `verifyProof`/circuit constraints (`inTotal + amountChanges === outTotal`, `OverflowPreventer`) only balance amounts, they never enforce commitment uniqueness across outputs.
- `rootHashExists` only checks the historic root is known; it says nothing about duplicate leaves within that root.
- `insertNullifiers`'s zero-skip (`if (inputNullifiers[i][j] != 0)`) is not itself the trigger here (that's the "zero-nullifier skip" branch, which is a separate/no-op path), the actual root cause is the collision of two *non-zero* commitments/nullifiers.

### Impact Explanation
Once a duplicate-preimage pair of outputs exists, one of the two equal-value leaves becomes permanently unspendable: its backing value remains locked in the `Hinkal` contract with no code path able to ever mark a matching nullifier, because the only nullifier value for that commitment/key pair is already consumed. This matches "Critical: permanent freezing of user funds" - the value was legitimately deposited (balance checks passed at creation) but can never be withdrawn by anyone, including the intended owner. The attacker can trigger this against their own funds (self-DoS, low interest) but the same mechanic can also be aimed at a third party by crafting a multi-output transaction with two duplicate outputs to a known recipient's stealth address, permanently freezing half of the value the attacker sends them, or a malicious relay/depositor scenario where a victim recipient never notices the duplicate before spending one copy.

### Likelihood Explanation
Preconditions are trivial and fully attacker-controlled: the attacker only needs to submit one valid `transact` call with `outputCount >= 2` for the same token index, matching `amount`, matching `publicKey` (their own or a known recipient's stealth address), and the shared `outTimeStamp` (which is a single circuit-wide signal already forced to be identical for every output in that call). No relay, no privileged role, no cross-chain assumptions, and no additional cost beyond the deposit itself are required. This is fully repeatable and 100% reliable once crafted; the "relay path / zero effective fee" branch mentioned in the question is not necessary to trigger the collision - it is a red herring relative to the actual root cause, which lives purely in the commitment/nullifier circuit design.

### Recommendation
Add per-output entropy to the commitment preimage (e.g., a random blinding factor or a running per-transaction output counter/leaf-index binding) so that two outputs with identical `(amount, token, publicKey, timeStamp)` are cryptographically distinct commitments and nullifiers. Additionally, add an on-chain uniqueness check across `circomData.outCommitments` within a single `transact` call (and ideally against previously seen leaves) to reject duplicate leaves before they are inserted into the tree.

### Proof of Concept
Foundry/Hardhat test plan:
1. Deploy `Hinkal` + circuits with a small `tokenCount/outputCount` circuit build.
2. Craft a `transact` call with `outputCount = 2`, both outputs for the same `erc20TokenAddresses[i]`, identical `outAmounts[i][0] == outAmounts[i][1]`, identical `outPublicKeys[i][0] == outPublicKeys[i][1]`, and rely on the shared `outTimeStamp` signal. Generate a locally computed valid Groth16 proof satisfying `inTotal + amountChanges === outTotal`.
3. Submit the transaction; assert `outCommitments[i][0] == outCommitments[i][1]` and that both leaves are inserted (`insertMany` called with two identical leaf values, verified via `NewCommitment` events).
4. Generate a spend proof for leaf index 0 (input UTXO matching the first output), submit `transact`; assert success and `nullifiers[N] == true`.
5. Generate a second, independent spend proof for leaf index 1 (same commitment value, different Merkle siblings/path), submit `transact`; assert the call reverts with `"Nullifier cannot be reused"`.
6. Assert that the contract's token balance corresponding to the second leaf's value remains locked (no code path lets it be withdrawn), demonstrating permanent freezing of backed value equal to `outAmounts[i][1]`.

### Citations

**File:** circuits/OriginalCommitmentCalculator.circom (L6-23)
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
}
```

**File:** circuits/Signature.circom (L5-14)
```text
template Signature() {
    signal input nullifyingPrivateKey;
    signal input commitment;
    signal output out;

    component hasher = Poseidon(2);
    hasher.inputs[0] <== nullifyingPrivateKey;
    hasher.inputs[1] <== commitment;
    out <== hasher.out;
}
```

**File:** circuits/NullifierCalculator.circom (L6-19)
```text
template NullifierCalculator() {
  signal input commitment;
  signal input signature;
  signal output out;

  component calcOriginalNullifier = Poseidon(2);
  calcOriginalNullifier.inputs[0] <== commitment;
  calcOriginalNullifier.inputs[1] <== signature;

  component calcCommitmentIsZero = IsZero();
  calcCommitmentIsZero.in <== commitment;

  out <== calcOriginalNullifier.out * (1 - calcCommitmentIsZero.out);
}
```

**File:** circuits/MainEVMCircuit.circom (L47-60)
```text
  signal input outAmounts[tokenCount][outputCount];
  signal input outTimeStamp;
  signal input outPublicKeys[tokenCount][outputCount];
  signal input outCommitments[tokenCount][outputCount];

  signal input calldataHash;

  signal input messageSeed;

  signal input H0Ax; // for creating a stealth address
  signal input H0Ay; // for creating a stealth address
  signal output outH1Ax;
  signal output outH1Ay;
  signal output outStealthAddress;
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

**File:** contracts/HinkalHelper.sol (L173-236)
```text
    function checkOnchainCreation(
        CircomData calldata circomData
    ) internal pure {
        bool isInternalTransaction = circomData
            .externalActionData
            .externalActionId == 0;

        for (uint i = 0; i < circomData.onChainCreation.length; i++) {
            if (circomData.onChainCreation[i]) {
                require(
                    !isInternalTransaction,
                    "onChainCreation not allowed for internal transactions"
                );
                require(
                    circomData.amountChanges[i] == 0,
                    "amountChanges must be zero when onChainCreation is true"
                );
                for (
                    uint j = 0;
                    j < circomData.inputNullifiers[i].length;
                    j++
                ) {
                    require(
                        circomData.inputNullifiers[i][j] == 0,
                        "inputNullifiers must be zero when onChainCreation is true"
                    );
                }
            }
        }
    }

    ///@notice make performance checks for transactions
    ///@dev Check if transacaction is valid before making it
    ///@param circomData circom data
    ///@return inputForCircom
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

**File:** contracts/HinkalBase.sol (L135-152)
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
        }
    }
```
