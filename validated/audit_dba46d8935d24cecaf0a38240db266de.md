This confirms the vulnerability. The nullifier is computed purely as `Poseidon(commitment, signature)` with no dependency on the leaf's tree index or Merkle path [1](#0-0) , and the commitment itself is `hash4(amount, token, stealthAddress, timeStamp)` [2](#0-1) . Since `timeStamp` is stamped as `block.timestamp` at deposit time [3](#0-2) , two `prooflessDeposit` calls in the same block with identical `amount`, `erc20Address`, and `stealthAddress` produce identical commitments, which get inserted as two distinct leaves via `insertMany` [4](#0-3) . Spending one leaf computes and marks nullifier `n` in `nullifiers` mapping [5](#0-4) , permanently blocking any future spend of the second, identical-commitment leaf since it maps to the same `n`.

### Title
Same-block `prooflessDeposit` collisions produce duplicate commitments/nullifiers, permanently freezing one leaf's funds - (File: contracts/Hinkal.sol, contracts/HinkalBase.sol, circuits/NullifierCalculator.circom)

### Summary
`_createProoflessDepositCommitments` derives each leaf's commitment from `hash4(amount, token, stealthAddress, block.timestamp)` with no per-deposit nonce or leaf-index binding. Two `prooflessDeposit` calls in the same block with identical `(amount, token, stealthAddress)` yield identical commitments at two different tree indices, and since the nullifier is `Poseidon(commitment, signature)` — independent of leaf index/path — both leaves collapse to the same nullifier, so spending one permanently freezes the other.

### Finding Description
The broken equality: two distinct Merkle leaves at different `insertedIndexes` should map to two distinct, independently spendable nullifiers, but here `leaf_1 == leaf_2` (same commitment) implies `nullifier(leaf_1) == nullifier(leaf_2)` for the same owner key/signature.

Path: attacker calls `Hinkal.prooflessDeposit` twice in one block (same tx via multicall or two txs in the same block) with identical `erc20Addresses[i]`, `amounts[i]`, and `stealthAddressStructures[i]` (self-funded, attacker's own stealth address both times). `_createProoflessDepositCommitments` computes `commitment = hash4(amount, token, stealthAddress, block.timestamp)` for each call [3](#0-2) , which is identical across both calls since `block.timestamp` is the same. `insertCommitments` inserts both as separate leaves via `insertMany` at two different `insertedIndexes`, emitting two `NewCommitment` events with the same leaf value but distinct negative indices [6](#0-5) .

The nullifier used when spending via `transact`/`insertNullifiers` is `Poseidon(commitment, signature)`, computed in-circuit by `NullifierCalculator`, with `signature` derived from the owner's private key over the commitment — no leaf index or Merkle path is folded in [1](#0-0) . Because both leaves share the same commitment and belong to the same stealth key, they produce the identical nullifier `n`. When the attacker spends the first leaf, `insertNullifiers` sets `nullifiers[n] = true` [5](#0-4) . Any subsequent proof attempting to spend the second leaf — which necessarily also computes nullifier `n` — reverts with `"Nullifier cannot be reused"`, permanently freezing that leaf's funds even though it was never spent and its Merkle root/path are still valid.

None of the existing guards prevent this: `rootHashExists`/root checks validate the leaf is in the tree (it is), `verifyProof` only proves knowledge of a valid pre-image and correct arithmetic (both are satisfied honestly for the duplicate leaf), and `insertNullifiers`'s only defense is the boolean flag on `n` itself, which by construction is shared.

### Impact Explanation
The attacker's own genuinely-deposited funds get permanently and unrecoverably frozen (self-inflicted here), but this demonstrates the underlying commitment/nullifier collision is trivially reachable by any unprivileged EOA with no proof requirement for the deposit step. The same collision generalizes: if any two leaves system-wide (including a relay/protocol fee UTXO created via `EmporiumUpgradeable.handleOut` or the relay-fee path in `Hinkal`'s `transact`, or two ordinary user deposits that coincidentally match `amount/token/stealthAddress` in the same block) end up with an identical `(amount, token, stealthAddress, timeStamp)` tuple, spending either one permanently freezes the other. This can freeze protocol/relay fee funds without any privileged action, matching "permanent freezing of user funds" (Critical) and, for relay/protocol fee UTXOs specifically, "permanent freezing of protocol/relay fees" (High).

### Likelihood Explanation
Preconditions are trivially satisfiable: `prooflessDeposit` requires no proof, is callable by any EOA, and same-block same-timestamp collisions are achievable at will via a single multicall transaction or by submitting two transactions and having them land in the same block (attacker can also just bundle both calls in one tx to guarantee this). No relay, admin, or third-party cooperation is needed to demonstrate the bug (self-targeted), and the cost is only the price of the duplicated deposit amount plus gas. Extending this to freeze relay/protocol fee UTXOs requires the attacker to engineer a `transact` such that the resulting relay-fee UTXO's `(amount, token, stealthAddress, timeStamp)` collides with another leaf in the same block — feasible since amounts and stealth addresses in a relay-fee UTXO are attacker-influenced via `CircomData`/fee parameters in many configurations, though this specific sub-path was not independently traced end-to-end in this session.

### Recommendation
Bind each on-chain-created commitment to a unique, unpredictable-to-collide value in addition to `(amount, token, stealthAddress, timeStamp)` — e.g., include the pre-insertion leaf index / a monotonically increasing per-tree nonce, or a per-deposit random blinding factor supplied by the depositor, in the `hash4` commitment preimage (and correspondingly in the nullifier derivation circuit, or ensure the nullifier calculation already depends on a per-UTXO blinding factor rather than solely on amount/token/stealthAddress/timestamp). This guarantees commitment (and thus nullifier) uniqueness across leaves regardless of timestamp collisions.

### Proof of Concept
Hardhat test:
1. Deploy Hinkal with a test ERC20; attacker EOA mints/approves twice the deposit amount.
2. In a single transaction (or forced same-block via `evm_setAutomine`/`hardhat_mine` batching), call `prooflessDeposit` twice with identical `erc20Addresses`, `amounts`, and `stealthAddressStructures` (attacker's own stealth address), differing only in call order.
3. Capture both `NewCommitment` events; assert `leaves[0] == leaves[1]` (identical commitment value) while `insertedIndexes[0] != insertedIndexes[1]`.
4. Generate a valid proof (locally, via snarkjs/circom test harness) to spend the first leaf via `transact`, using the attacker's stealth private key; call `transact` and assert success, and assert `nullifiers[n] == true` afterward.
5. Generate a second valid proof to spend the second leaf (identical commitment ⇒ identical nullifier `n`); call `transact` and assert it reverts with `"Nullifier cannot be reused"`, proving the second, fully-funded, never-spent leaf is permanently unspendable.

### Citations

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

**File:** contracts/HinkalBase.sol (L100-131)
```text
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

**File:** contracts/Hinkal.sol (L336-346)
```text
        for (uint256 i = 0; i < length; i++) {
            onChainCommitmentsArray[i] = createOnchainCommitment(
                UTXO({
                    amount: amounts[i],
                    erc20Address: erc20Addresses[i],
                    stealthAddressStructure: stealthAddressStructures[i],
                    timeStamp: block.timestamp
                }),
                onChainEncryptedOutputs[i]
            );
        }
```
