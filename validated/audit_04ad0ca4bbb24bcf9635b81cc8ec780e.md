### Title
Reused `onChainCreation` flag lets a per-token "on-chain output" marker suppress insertion of *input* nullifiers, enabling nullifier/UTXO reuse - (File: contracts/HinkalBase.sol)

### Summary
`HinkalBase.insertNullifiers` reuses the same `onChainCreation` boolean array that `insertCommitments` correctly uses to decide *output*-creation mode, but applies it to gate whether *input* nullifiers for that token index are marked spent at all. This is structurally the same bug class as the reported Phuture finding: a boolean meant to select/skip one category of asset handling is also (mis)applied to a different category of the same accounting loop, breaking the equality between "nullifier verified valid by the ZK proof" and "nullifier recorded as spent on-chain."

### Finding Description
`CircomData.onChainCreation` is a `bool[]` indexed by token (aligned with `erc20TokenAddresses`, `amountChanges`, `inputNullifiers`, `outCommitments`), used in `Hinkal.sol` `_transact` purely to decide whether a token's **output** amount change is accounted for off-chain (`amountChanges[i]`) or via the separately-returned on-chain `utxoSet` [1](#0-0) .

The same flag is reused in `insertCommitments` to skip iterating `offChainCommitments[i]` when the output for token `i` was created on-chain instead [2](#0-1)  — this usage is self-consistent because it only controls the *output* side.

However, `insertNullifiers` also uses `onChainCreation[i]` to `break` out of the inner loop over `inputNullifiers[i][j]`, meaning that if `onChainCreation[i] == true` for a token index, **none of that token's input nullifiers are ever marked as spent, and no `Nullified` event is emitted**, regardless of how many non-zero input nullifiers are present: [3](#0-2) 

The ZK circuit (`MainEVMCircuit.circom`) verifies that each `inNullifiers[i][j]` is correctly derived from a valid, Merkle-included commitment for token `i` and that `inTotal + amountChanges[i] === outTotal` for the token [4](#0-3) , but the circuit's role is limited to proving the *arithmetic and ownership* validity of the supplied nullifiers — it does not, and cannot, enforce that the Solidity contract actually records those nullifiers as spent afterward. That bookkeeping is entirely delegated to `insertNullifiers`.

Because `onChainCreation[i]` is semantically about the *output* for token `i` (whether it's created on-chain), nothing prevents a caller from simultaneously supplying valid, non-zero `inputNullifiers[i]` (spending real input UTXOs of token `i`) while setting `onChainCreation[i] = true` for that same token index. If so, `insertNullifiers` silently skips recording those nullifiers as spent, even though the proof confirms they encode legitimate, unspent balance. The equality broken is: **"nullifier accepted by the verifier" should imply "nullifier permanently marked spent in the `nullifiers` mapping"** — this analog breaks that equality in the same way the Phuture bug broke "asset excluded from mint check" vs "asset excluded from burn check."

### Impact Explanation
If exploitable, this is a **nullifier verification bypass enabling double-spend of shielded UTXOs**: an attacker could repeatedly submit the same input nullifiers/commitment across multiple `transact()` calls (each time marking `onChainCreation[i] = true` for the affected token index), draining more value out via `amountChanges`/`utxoSet`/withdrawal than was ever actually deposited/held, directly analogous to the original finding's "get funds back without ever depositing." This matches the Critical impact category of "proof or nullifier verification bypass" / "double spend."

### Likelihood Explanation
This depends on whether `HinkalHelper.performHinkalChecks` (called before `_transact`'s side effects) independently enforces that `inputNullifiers[i]` must be all-zero whenever `onChainCreation[i]` is true for the same index. I was not able to fully inspect `HinkalHelper.sol`'s validation logic within the available tool budget, so I cannot confirm or rule out such a guard. If no such cross-field constraint exists in `HinkalHelper` or the circuit's public-input construction, the bypass is directly reachable by any unprivileged EOA constructing a valid proof with non-zero input nullifiers for a token index it also flags as `onChainCreation = true`.

### Recommendation
- In `insertNullifiers`, do not gate nullifier insertion on `onChainCreation[i]`; input nullifiers must always be recorded when non-zero, independent of how that token's *output* is created.
- Alternatively, if the intent is that `onChainCreation[i] == true` implies "no inputs are spent for token `i`," this invariant must be explicitly enforced in `HinkalHelper.performHinkalChecks` (e.g., require all `inputNullifiers[i][j] == 0` whenever `onChainCreation[i]` is true) or as a circuit constraint, so the Solidity bookkeeping cannot silently diverge from the proof's guarantees.

### Proof of Concept
1. Attacker deposits a UTXO of token `T` at array index `i` and later builds a valid proof/`CircomData` spending that UTXO's nullifier (`inputNullifiers[i] = [validNullifier]`), withdrawing the value via `amountChanges[i]`.
2. Attacker sets `onChainCreation[i] = true` for that same index (a field otherwise meant only to indicate the token's *output* is created on-chain instead of off-chain).
3. `Hinkal.transact` verifies the proof and root hash, then calls `insertNullifiers`, whose inner loop hits `if (onChainCreation[i] == true) break;` before reaching the non-zero nullifier check [5](#0-4) , so `nullifiers[validNullifier]` is never set to `true`.
4. The attacker repeats step 1–3 with the identical nullifier/commitment in a subsequent `transact()` call; since it was never marked spent, `insertNullifiers`'s `require(!nullifiers[...])` check never reverts, allowing the same UTXO to be withdrawn again.

### Citations

**File:** contracts/Hinkal.sol (L137-146)
```text
                require(
                    balanceDif ==
                        (
                            circomData.onChainCreation[i]
                                ? int256(0)
                                : circomData.amountChanges[i]
                        ) +
                            int256(utxoAmount),
                    "Balance Diff Should be equal to sum of onchain and offchain created commitments"
                );
```

**File:** contracts/HinkalBase.sol (L80-99)
```text
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

**File:** circuits/MainEVMCircuit.circom (L129-168)
```text
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
```
