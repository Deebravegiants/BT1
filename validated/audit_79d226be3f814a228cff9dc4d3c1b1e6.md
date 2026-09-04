### Title
Duplicate on-chain commitments from `EmporiumUpgradeable.handleOut` share one nullifier, permanently freezing the second UTXO - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.handleOut` builds the output `UTXO` from caller-controlled `circomData.timeStamp` and `circomData.stealthAddressStructure` with no uniqueness enforcement across separate `runAction`/`transact` calls. Because the on-chain commitment `hash4(amount, erc20Address, stealthAddress, timeStamp)` and the corresponding nullifier `Poseidon(commitment, Poseidon(nullifyingPrivateKey, commitment))` are both pure functions of these four values (and the spender's private key) with no dependency on the Merkle leaf index, two separate `runAction` calls that reproduce the same `(amount, erc20Address, stealthAddress, timeStamp)` tuple create two distinct tree leaves that collapse to the identical nullifier. Spending the first leaf permanently prevents spending the second.

### Finding Description
The equality broken is: **commitment_A == commitment_B ⇒ nullifier_A == nullifier_B**, even though leaf_A and leaf_B occupy different Merkle indices.

- `handleOut` constructs `UTXO(uint256(balanceChange), erc20TokenAddresses[i], circomData.stealthAddressStructure, circomData.timeStamp)` [1](#0-0) . `circomData.timeStamp` and `circomData.stealthAddressStructure` are fully caller-supplied public inputs on `CircomData` [2](#0-1) , and nothing on the `runAction`/`handleOut` path ties `timeStamp` to `block.timestamp`, a nonce, or any per-call unique salt.
- The Merkle leaf is `hash4(utxo.amount, uint256(uint160(utxo.erc20Address)), utxo.stealthAddressStructure.stealthAddress, utxo.timeStamp)`, computed in `createOnchainCommitment` [3](#0-2) . If two `runAction` calls produce the same `(amount, erc20Address, stealthAddress, timeStamp)` — which the attacker can force by controlling `op.endpoint`/`op.callData` (to make `balanceChange` deterministic) and reusing the same `timeStamp`/`stealthAddressStructure` — the two leaves have identical commitment values.
- `insertCommitments` inserts these leaves with no duplicate check, simply appending them to the tree at new indices via `insertMany` [4](#0-3) .
- Critically, the nullifier used to later spend such a leaf is `NullifierCalculator`: `Poseidon(commitment, signature)` where `signature = Poseidon(nullifyingPrivateKey, commitment)` [5](#0-4) [6](#0-5) . Neither the commitment computation (`OriginalCommitmentCalculator`, `Poseidon(amount, erc20TokenAddress, publicKey, timeStamp)`) nor the nullifier computation reference the Merkle path or leaf index at all [7](#0-6) [8](#0-7) . The circuit only proves inclusion of *a* leaf with that commitment value via `MerkleRootCalculator` against the current `rootHashHinkal`, using an arbitrary sibling path chosen by the prover — it never binds the proof to a specific leaf index among multiple leaves sharing the same commitment.
- `insertNullifiers` only checks whether the specific nullifier value was previously marked used, not whether the *commitment being spent* is uniquely identified [9](#0-8) .

Consequently: after the attacker (or the payee themselves) spends leaf_A using nullifier_N, `nullifiers[N] = true`. Leaf_B, still unspent in the tree with a valid Merkle path and the exact same commitment, requires the identical nullifier_N to be spent (same commitment, same recipient nullifying key), which is now rejected by `insertNullifiers`'s `require(!nullifiers[...], "Nullifier cannot be reused")`. Leaf_B's value is permanently unspendable — a real fund freeze, not merely a duplicate/no-op leaf.

None of the existing guards catch this: `performHinkalChecks`/`dimensionsCheck` validate array shapes, not cross-call uniqueness; `verifyProof`/circuit constraints (`inTotal+amountChanges===outTotal`, `OverflowPreventer`, `ForceEqualIfEnabled`) validate a single transaction's internal balance/commitment consistency, not collisions across two independent transactions; `rootHashExists` only checks the root used for input-spend proofs, unrelated to output-leaf uniqueness; `EmporiumUpgradeable.verifyWallet`'s `usedMessages[circomData.emporiumMessage]` replay guard only prevents reusing the same `emporiumMessage`, not two distinct messages producing identical `(amount, erc20Address, stealthAddress, timeStamp)` outputs.

### Impact Explanation
The second identical on-chain UTXO becomes permanently frozen: its value can never be withdrawn because its unique spending nullifier is already consumed by the first identical leaf. This is a genuine "leaf stranded" / permanent freezing of user funds scenario. If the `stealthAddressStructure` targets a third-party payee (a normal usage pattern for stealth-address payments), the attacker who controls the `runAction` inputs can strand a victim recipient's second payout without the victim's consent — matching the Critical category ("permanent freezing of user funds"). This is repeatable for any pair of `runAction` calls the attacker can engineer to reproduce identical `(erc20TokenAddresses[i], balanceChange, timeStamp, stealthAddress)`.

### Likelihood Explanation
Preconditions are attacker-controllable and require no privileged role: EmporiumUpgradeable must be registered as an external action (already assumed true per the question), the attacker must be an `onlyAllowedRecipient` caller of `runAction` (a normal relay-invoked path reachable by any user submitting a `Hinkal.transact`), and must be able to make two separate `endpoint.call` sequences yield the identical numeric `balanceChange` for the same token — trivially achievable with a self-deployed mock/target endpoint or a deterministic swap/transfer amount. Reusing `circomData.timeStamp` and `stealthAddressStructure` across two calls costs nothing extra since these are plain calldata fields with no on-chain freshness check. The attack is fully repeatable and requires only two ordinary transactions.

### Recommendation
Bind uniqueness into the output commitment/leaf per creation event, e.g.:
- Enforce `circomData.timeStamp` monotonicity/uniqueness on-chain per `(stealthAddress, erc20TokenAddress)` pair (e.g., require `timeStamp == block.timestamp` or a strictly increasing per-recipient counter), or
- Mix a globally unique value (e.g., `insertedIndex`/leaf position, or a running on-chain nonce) into the commitment/nullifier derivation so identical `(amount, erc20Address, stealthAddress, timeStamp)` tuples cannot collide, or
- Add an explicit on-chain check in `insertCommitments`/`createOnchainCommitment` rejecting a newly computed leaf value that already exists in the tree (duplicate-commitment guard) before insertion.

### Proof of Concept
Foundry fork test plan:
1. Deploy `EmporiumUpgradeable`, a mock ERC20, and a mock endpoint contract whose `call` always increases the Emporium's token balance by a fixed `AMOUNT`.
2. Build `CircomData` #1 with `erc20TokenAddresses = [token]`, `stealthAddressStructure = S`, `timeStamp = T`, `externalActionData` pointing to an `EmporiumStack` with one op calling the mock endpoint; call `Hinkal.transact` (or `runAction` directly if reachable) — capture the emitted `NewCommitment` leaf value `L1`.
3. Repeat step 2 with a fresh `emporiumMessage` but identical `T`, `S`, and endpoint call producing the same `AMOUNT` — capture leaf `L2`.
4. Assert `L1 == L2` (equality claimed broken).
5. Using the recipient's `nullifyingPrivateKey` for `S`, generate a locally computed proof spending `L1` via `Hinkal.transact`; assert success and that `nullifiers[N]` becomes `true` for the derived nullifier `N`.
6. Attempt to generate and submit a proof spending `L2` (same commitment, same private key ⇒ same `N`); assert it reverts with `"Nullifier cannot be reused"`, proving the second identical UTXO is permanently frozen despite being a distinct, valid, unspent tree leaf.

### Citations

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

**File:** contracts/types/CircomData.sol (L23-45)
```text
struct CircomData {
    uint256 rootHashHinkal;
    uint256 rootHashHinkalIndex;
    address[] erc20TokenAddresses;
    int256[] amountChanges;
    uint256[][] inputNullifiers;
    uint256[][] outCommitments;
    bytes[][] encryptedOutputs;
    bytes onChainEncryptedOutput;
    bool[] onChainCreation;
    int256[] slippageValues;
    FeeStructure feeStructure;
    StealthAddressStructure stealthAddressStructure;
    uint256 timeStamp;
    uint256 calldataHash;
    uint256 emporiumMessage;
    uint16 publicSignalCount;
    address relay;
    ExternalActionData externalActionData;
    HookData hookData;
    address originalSender;
    bytes extraData;
}
```

**File:** contracts/HinkalBase.sol (L53-70)
```text
    function createOnchainCommitment(
        UTXO memory utxo,
        bytes calldata onChainEncryptedOutput
    ) internal view returns (OnChainCommitment memory) {
        uint256 commitment = hash4(
            utxo.amount,
            uint256(uint160(utxo.erc20Address)),
            utxo.stealthAddressStructure.stealthAddress,
            utxo.timeStamp
        );

        OnChainCommitment memory onChainCommitment = OnChainCommitment({
            utxo: utxo,
            commitment: commitment,
            onChainEncryptedOutput: onChainEncryptedOutput
        });
        return onChainCommitment;
    }
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

**File:** circuits/NullifierCalculator.circom (L1-19)
```text
pragma circom 2.1.6;

include "../../node_modules/circomlib/circuits/poseidon.circom";
include "../../node_modules/circomlib/circuits/comparators.circom";

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

**File:** circuits/Signature.circom (L1-14)
```text
pragma circom 2.1.6;

include "../../node_modules/circomlib/circuits/poseidon.circom";

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

**File:** circuits/OriginalCommitmentCalculator.circom (L1-22)
```text
pragma circom 2.1.6;

include "../../node_modules/circomlib/circuits/poseidon.circom";
include "../../node_modules/circomlib/circuits/comparators.circom";

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

**File:** circuits/MainEVMCircuit.circom (L114-150)
```text
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
```
