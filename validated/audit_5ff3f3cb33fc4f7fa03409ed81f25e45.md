### Title
Off-chain output commitments are silently dropped from the Merkle tree whenever `onChainCreation[i]` is true, while nothing on-chain enforces those commitments to be zero - ([File: contracts/HinkalBase.sol])

### Summary
`insertCommitments` (contracts/HinkalBase.sol:72-133) breaks out of the inner `j` loop the instant `onChainCreation[i]` is true, so any `offChainCommitments[i][j]` values for that token index are never counted, never inserted into the tree, and never emitted via `NewCommitment` - even if they are nonzero. `checkOnchainCreation` (contracts/HinkalHelper.sol:173-202) validates `amountChanges[i]==0` and all `inputNullifiers[i][j]==0` when `onChainCreation[i]` is true, but conspicuously never validates that `outCommitments[i][j]` (the calldata that becomes `offChainCommitments`) is also zero for that index.

### Finding Description
The equality that should hold is: **every nonzero leaf value present in `circomData.outCommitments[i][j]` must be inserted into the Merkle tree** (TREE TRUTH). Tracing the code:

- `insertCommitments` computes `length` by iterating `offChainCommitments[i][j]`, but `if (onChainCreation[i]) break;` (contracts/HinkalBase.sol:82) exits the `j` loop unconditionally for that `i`, regardless of the actual value of `offChainCommitments[i][j]`. The same `break` is repeated in the leaf-flattening loop (line 94) and the emission loop (line 111).
- `checkOnchainCreation` (contracts/HinkalHelper.sol:173-202) is the only guard that runs before `insertCommitments`, and it enforces:
  - `amountChanges[i] == 0` when `onChainCreation[i]` is true
  - `inputNullifiers[i][j] == 0` for all `j` when `onChainCreation[i]` is true

  It does **not** assert `outCommitments[i][j] == 0` for `onChainCreation[i] == true`. This is an asymmetry: the two other arrays keyed by token index (`amountChanges`, `inputNullifiers`) are defensively zero-checked, but `outCommitments` is not.
- The balance equation in `Hinkal.sol:137-146` only reconciles `balanceDif` against `amountChanges[i]` (forced to 0) plus `utxoAmount` (from on-chain UTXOs) - it never references `offChainCommitments`/`outCommitments` directly, so a nonzero value sitting in `outCommitments[i][j]` for an `onChainCreation[i]=true` slot has no on-chain balance check tying it to anything.

If the underlying circuit computation for a given output slot can produce a nonzero commitment hash (e.g., `hash4(amount, erc20Address, stealthAddress, blinding/timestamp)`) even when the encoded amount is 0 - which is plausible since Poseidon-style hashes of zero amount with nonzero stealth-address/blinding fields are not themselves zero - then a validly-proved transaction can carry a nonzero `outCommitments[i][j]` under `onChainCreation[i]=true`. That value is a public input the circuit and verifier accept as valid, yet `insertCommitments` drops it entirely: no leaf is inserted, no `NewCommitment` event fires, and the value is unrecoverable (no leaf, no nullifier path can ever be built for it).

### Impact Explanation
If exploitable, the impact is Critical: permanent freezing/stranding of user funds. A user (attacker or otherwise) who submits a transaction where the circuit encodes real value into `outCommitments[i][j]` for a token index simultaneously flagged `onChainCreation[i]=true` would have that value permanently excluded from the spendable set (no tree leaf exists to build a future nullifier/withdraw proof against), while the transaction as a whole succeeds and is accepted as valid by the contract.

### Likelihood Explanation
The contract-level gap is concretely confirmed: `checkOnchainCreation` (contracts/HinkalHelper.sol:173-202) does not zero-check `outCommitments[i][j]`, and `insertCommitments`'s `break` logic (contracts/HinkalBase.sol:82,94,111) unconditionally discards the rest of that row regardless of content. What is not verified in this pass is whether the paired circuit constraints (`circuits/**`, out of my available read budget this session) additionally force `outCommitments[i][j] == 0` whenever `onChainCreation[i] == true` and `amountChanges[i] == 0`/no inputs are consumed - if the circuit itself enforces `outTotal == inTotal + amountChanges == 0` and separately forces the commitment hash to literal 0 for unused/zero-amount output slots (which is the established sentinel convention used elsewhere in this codebase, per the `!= 0` checks throughout `insertCommitments`/`insertNullifiers`), then a legitimately-generated proof could never actually present a nonzero `outCommitments[i][j]` in this configuration, closing off the practical exploit path even though the Solidity-side guard is missing. This uncertainty should be resolved by inspecting the main transact circuit (not the excluded `BabyJubjubConstants.circom`) before treating this as confirmed exploitable end-to-end.

### Recommendation
Add an explicit contract-side guard in `checkOnchainCreation` mirroring the existing `amountChanges`/`inputNullifiers` checks: require `circomData.outCommitments[i][j] == 0` for all `j` whenever `onChainCreation[i]` is true. Additionally, fix `insertCommitments` to not rely on `break` as an implicit "skip" - even with the added guard, defense-in-depth suggests iterating with `continue`/explicit zero-checks rather than trusting that `onChainCreation[i]` implies no further nonzero entries exist in that row, so a future change to `onChainCreation` semantics cannot silently reintroduce leaf loss.

### Proof of Concept
Foundry test plan (contingent on being able to craft a valid proof, or by stubbing the verifier in a fork/mock to isolate the contract-logic bug):
1. Deploy `Hinkal` with a mock verifier that accepts any proof (or use the real verifier with a locally generated proof where the circuit is shown to permit nonzero `outCommitments[i][j]` alongside `onChainCreation[i]=true`).
2. Call `transact` with `circomData.onChainCreation[i] = true`, `circomData.amountChanges[i] = 0`, `circomData.inputNullifiers[i][*] = 0` (satisfying `checkOnchainCreation`), but `circomData.outCommitments[i][0] = X` for some nonzero `X`.
3. Assert LHS: `X` is present in `circomData.outCommitments[i][0]` (nonzero, as submitted/committed by the proof's public inputs).
4. Assert RHS: after the call, no `NewCommitment` event was emitted for `X`, and `X` is not a leaf in the Merkle tree (e.g., via `Merkle`'s leaf-lookup/root recomputation not containing `X`).
5. Demonstrate LHS ≠ RHS - the value `X` the circuit publicly committed to is never inserted, proving the stranding. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

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

**File:** contracts/HinkalHelper.sol (L173-202)
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
```

**File:** contracts/Hinkal.sol (L134-147)
```text
                // balance equation to check: CHANGE IN BALANCE SHOULD EQUAL TO
                // 1) change in off-chain utxos
                // 2) change in on-chain utxos
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
            }
```

**File:** contracts/Hinkal.sol (L156-166)
```text
            insertNullifiers(
                circomData.inputNullifiers,
                circomData.onChainCreation
            );

            insertCommitments(
                circomData.outCommitments,
                circomData.encryptedOutputs,
                onChainCommitments,
                circomData.onChainCreation
            );
```
