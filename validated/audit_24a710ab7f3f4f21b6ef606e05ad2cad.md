### Title
Nullifiers are never checked/recorded for token groups flagged `onChainCreation`, enabling double-spend of off-chain UTXOs - (File: `contracts/HinkalBase.sol`)

### Summary
`HinkalBase.insertNullifiers` skips nullifier validation and insertion entirely for any index `i` where `circomData.onChainCreation[i] == true`, instead of skipping only when the corresponding nullifier value is `0`. This lets a caller mark a token group as "on-chain creation" while still supplying real, non-zero input nullifiers for that group, causing the on-chain double-spend guard to never fire for those nullifiers.

### Finding Description
`insertNullifiers` is the function responsible for enforcing the core "spend once" invariant of the UTXO model — every input nullifier consumed by a `transact()` call must be checked against the `nullifiers` mapping and then marked spent: [1](#0-0) 

Note the `break` on `onChainCreation[i] == true` inside the inner loop, *before* the `inputNullifiers[i][j] != 0` check. This means: for any index `i` in the per-token arrays (`erc20TokenAddresses`, `amountChanges`, `inputNullifiers`, `outCommitments`, `onChainCreation`) where the caller sets `onChainCreation[i] = true`, the entire inner array `inputNullifiers[i]` is skipped — the `require(!nullifiers[...])` check never runs and `nullifiers[...] = true` is never set, regardless of whether `inputNullifiers[i]` actually contains real, non-zero nullifiers for UTXOs being spent.

Compare this with `insertCommitments`, which uses the identical `onChainCreation[i]` flag purely to decide whether *output* commitments for that group are constructed on-chain vs. off-chain [2](#0-1) . Nothing in `CircomData`, `CircomDataBuilder.formBasicInput`, or `Hinkal.transact` forces `inputNullifiers[i]` to be all-zero when `onChainCreation[i]` is true — the circuit's public-input vector still includes whatever nullifier values are placed in `circomData.inputNullifiers[i][j]` [3](#0-2) , and `Hinkal.transact` treats `onChainCreation[i]` only as an output-side toggle when computing the balance equation [4](#0-3) .

The ZK proof itself only proves that the prover knows a valid opening for a UTXO whose commitment exists in the tree and that the claimed nullifier is correctly derived from it — the proof system does not, and cannot by itself, prevent the same valid nullifier from being submitted again in a later transaction. That protection is exclusively the job of the on-chain `nullifiers` mapping check in `insertNullifiers`. By setting `onChainCreation[i] = true` for the group containing a genuine input nullifier, an attacker bypasses that check entirely and can resubmit the same valid proof/nullifier in a subsequent `transact()` call, spending the same off-chain UTXO multiple times.

This breaks the double-spend equality the protocol relies on: "each nullifier may be redeemed for value exactly once." After the exploit, the attacker has withdrawn/transferred value corresponding to the same input UTXO N times while it was only ever backed once in the tree — unbacked value is created (equivalent to minting shielded value without backing), directly analogous to the reported `HoldefiPrices.addStableCoin` issue where a critical state value could be reset/reused without checking prior existence.

### Impact Explanation
This is a critical-severity issue: it permits double-spending a shielded UTXO, i.e., minting value not backed by a real deposit and directly stealing protocol funds (the contract's token balance would eventually be drained beyond what deposits actually back). This matches the "Critical" impact bucket: double spend / minting shielded value without backing / proof-nullifier verification bypass.

### Likelihood Explanation
Reachable by any unprivileged EOA/relayer with a single valid Groth16 proof for one legitimate deposit UTXO: the attacker only needs to set `onChainCreation[i] = true` for the token index carrying that input nullifier while keeping the rest of the transaction internally consistent enough to pass `HinkalHelper.performHinkalChecks` and the proof verification. No admin/owner/relay key is required — this is entirely within a normal user's control over their own `CircomData` payload.

### Recommendation
In `insertNullifiers`, do not use `onChainCreation[i]` to skip nullifier processing. Iterate and enforce/insert every non-zero entry in `inputNullifiers[i][j]` unconditionally (mirroring the semantics that `onChainCreation` should only affect where *outputs* are created, not whether *inputs* are checked for reuse):
```solidity
function insertNullifiers(
    uint256[][] calldata inputNullifiers,
    bool[] calldata onChainCreation
) internal {
    for (uint256 i = 0; i < inputNullifiers.length; i++) {
        for (uint256 j = 0; j < inputNullifiers[i].length; j++) {
            if (inputNullifiers[i][j] != 0) {
                require(!nullifiers[inputNullifiers[i][j]], "Nullifier cannot be reused");
                nullifiers[inputNullifiers[i][j]] = true;
                emit Nullified(inputNullifiers[i][j]);
            }
        }
    }
}
```
If `onChainCreation` truly implies "no inputs are ever spent for this group" by circuit design, that invariant should additionally be enforced on-chain (e.g., `require(onChainCreation[i] == false || inputNullifiers[i] are all zero)`), rather than silently trusting it.

### Proof of Concept
1. Attacker deposits a UTXO of amount `X` for token `T` (creates commitment `C` in the tree, e.g. via `prooflessDeposit`).
2. Attacker generates a valid proof for `transact()` that spends `C` (produces nullifier `N` for `C`) and withdraws/transfers value `X`, placing `T`, the amount, and `N` at array index `i`, but sets `circomData.onChainCreation[i] = true`.
3. `Hinkal.transact` verifies the proof and balance equation successfully (both are self-consistent for this single call), executes the transfer of `X`, and calls `insertNullifiers`.
4. Because `onChainCreation[i] == true`, the inner loop `break`s before checking/inserting `N`; `nullifiers[N]` remains `false`.
5. Attacker repeats step 2–4 with the same proof/`circomData` (or a freshly generated proof reusing the same nullifier `N`) any number of times. Each call passes because `nullifiers[N]` was never set, withdrawing `X` again each time — total value extracted becomes `k * X` for `k` repetitions, while only `X` was ever deposited.

Note: I could not fully trace the exact `Dimensions`/index-mapping conventions produced by the off-chain SDK/circuit templates (`circuits/**` code that builds `inputNullifiers` vs. `onChainCreation` arrays) within the index available to me, so I cannot 100% rule out an additional on-chain length/consistency check elsewhere that forces `inputNullifiers[i]` to be zero whenever `onChainCreation[i]` is true. Based on everything inspected in `contracts/HinkalHelper.sol`, `contracts/Hinkal.sol`, `contracts/HinkalBase.sol`, and `contracts/CircomDataBuilder.sol`, no such enforcement exists on-chain, and I'd recommend a full-repository review (e.g., a Devin session) to confirm this is not constrained elsewhere before treating it as fully validated.

### Citations

**File:** contracts/HinkalBase.sol (L72-102)
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

**File:** contracts/CircomDataBuilder.sol (L221-225)
```text
        for (uint16 i = 0; i < circomData.inputNullifiers.length; i++) {
            for (uint16 j = 0; j < circomData.inputNullifiers[i].length; j++) {
                input[index++] = circomData.inputNullifiers[i][j];
            }
        }
```

**File:** contracts/Hinkal.sol (L134-146)
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
```
