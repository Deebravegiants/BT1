### Title
`insertNullifiers` skips ALL input-nullifier bookkeeping for a token index when `onChainCreation[i]==true`, letting genuinely spent leaves be replayed - (`contracts/HinkalBase.sol:135-152`)

### Summary
`insertNullifiers` uses `break` on the per-token flag `onChainCreation[i]` at the top of the inner `j` loop, so as soon as `onChainCreation[i]==true` the loop exits at `j=0` and **no** `inputNullifiers[i][*]` are ever recorded, regardless of how many of them are real, non-zero nullifiers for genuinely spent leaves. Because `MainEVMCircuit.circom` never receives `onChainCreation` as a signal, it validates `inNullifiers[i][j] === calcNullifier[i][j].out` unconditionally, so a proof spending real UTXOs at token index `i` passes `verifyProof` even when `circomData.onChainCreation[i]` is set to `true`.

### Finding Description
Equality that must hold (SINGLE_SPEND): for every leaf `L` with nullifier `N`, once a proof is accepted where `inNullifiers[i][j] == N`, `nullifiers[N]` must become `true` so that `N` can never be accepted again. This equality is broken.

Code path:
- `circuits/MainEVMCircuit.circom:17-26` lists public/private params; `onChainCreation` is not among them - the circuit is blind to it. [1](#0-0) 
- `inNullifiers[i][j] === calcNullifier[i][j].out` is enforced for every `i,j` unconditionally. [2](#0-1) 
- On the Solidity side, `Hinkal.transact` calls `verifyProof` then, after the balance checks, calls `insertNullifiers(circomData.inputNullifiers, circomData.onChainCreation)`. [3](#0-2) 
- `insertNullifiers` breaks the inner loop on `onChainCreation[i]==true` regardless of `j`, so any nonzero `inputNullifiers[i][0..n]` for that token index are never checked, never marked `true` in `nullifiers`, and `Nullified` is never emitted. [4](#0-3) 

Attacker call sequence: deposit two (or more) real UTXOs of the same ERC20 at token index `i`; build a proof that spends both as `inputNullifiers[i][0]`, `inputNullifiers[i][1]` (real, matching `calcNullifier`), with `onChainCreation[i] = true`. `_calculateDeltaAmount`/the balance check zero out `amountChanges[i]` for that index when `onChainCreation[i]` is true, so `_internalTransact` performs no real transfer for that token and the balance requirement (`balanceDif == 0 + utxoAmount`) trivially holds when nothing moves for that index. [5](#0-4) [6](#0-5)  `verifyProof` succeeds because the circuit validates nullifier correctness independent of `onChainCreation`, and `insertNullifiers` then discards the record of both real nullifiers.

The result is that the two real leaves are proven "spent" (their secrets were used to build a valid nullifier and pass the merkle-root check gated by `ForceEqualIfEnabled` with `enabled <== inAmounts[i][j]`) yet `nullifiers[N]` is never flipped to `true`. The same calldata (or a fresh proof reusing the same nullifiers) can be resubmitted, and `require(!nullifiers[...], "Nullifier cannot be reused")` never fires for that token index, so the leaves remain spendable indefinitely - breaking the SINGLE_SPEND invariant this check exists to enforce.

None of the existing guards catch this: `performHinkalChecks`/`dimensionsCheck` validate array shapes, not the cross-field consistency between `onChainCreation` and non-zero `inputNullifiers` at the same index; `rootHashExists` only checks tree root freshness; the balance/slippage requires operate on token balances, not on nullifier bookkeeping; and the circuit constraints listed (`inTotal+amountChanges===outTotal`, `OverflowPreventer`, `ForceEqualIfEnabled`) never reference `onChainCreation` at all, so they cannot prevent the mismatch between "circuit says nullifier is valid" and "Solidity records nullifier as spent."

### Impact Explanation
This is a direct nullifier-verification bypass: a real, value-bearing leaf can be included in an accepted `transact()` call as a spent input without ever being marked spent on-chain. This satisfies the "proof or nullifier verification bypass" / "double spend" Critical category. The immediately demonstrable consequence (and the one specified in the question's proof idea) is that the identical proof/nullifiers can be replayed without the expected "Nullifier cannot be reused" revert, which is itself a critical breakage of the core spend-once guarantee the entire shielded-pool security model rests on. This is repeatable for every token index an attacker chooses to flag `onChainCreation=true` while embedding real nullifiers.

### Likelihood Explanation
Preconditions are attacker-controlled and unprivileged: own two or more real UTXOs of the same token at some index, and craft `circomData.onChainCreation[i]=true` while placing genuine `inputNullifiers[i][*]` for those UTXOs - all fields (`CircomData`, `Dimensions`) are explicitly listed as attacker-craftable in the threat model. No special role, whitelisted relay, or victim cooperation is needed. The only "cost" is generating a valid witness/proof for a legitimate transaction that happens to set the flag combination described - well within a single unprivileged party's capability.

### Recommendation
Decouple nullifier insertion from `onChainCreation`. `onChainCreation[i]` should only govern how *outputs* for token index `i` are committed (on-chain vs. off-chain); it has no legitimate bearing on whether *inputs* at index `i` were spent. Remove the `if (onChainCreation[i] == true) break;` check from `insertNullifiers`'s inner loop entirely, so every non-zero `inputNullifiers[i][j]` is always checked against `nullifiers` and recorded, regardless of the token's `onChainCreation` flag.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`/`HinkalHelper` stack; deposit two real UTXOs (`A`, `B`) of the same ERC20 at token index `i` for the attacker's stealth address.
2. Off-chain, generate a witness/proof for `MainEVMCircuit` that spends `A` and `B` as `inputNullifiers[i][0]`, `inputNullifiers[i][1]` with correct `calcNullifier` values and valid merkle paths (root check enabled since `inAmounts[i][j] != 0`), zero outputs for index `i` (`outAmounts[i][*]=0`), and any consistent `amountChanges[i]` (ignored by the on-chain balance check since `onChainCreation[i]=true`).
3. Build `circomData` with `onChainCreation[i] = true` for that index; call `Hinkal.transact(a,b,c,dimensions,circomData)`.
4. Assert the call succeeds (`verifyProof` passes, balance checks pass because `_calculateDeltaAmount` returns 0 for index `i`).
5. Assert `nullifiers[inputNullifiers[i][0]] == false` and `nullifiers[inputNullifiers[i][1]] == false` after the call (equality broken: nullifier "spent" in the proof but `nullifiers[N] != true` on-chain).
6. Call `transact` again with the same `a,b,c,circomData` (or a fresh proof reusing the same nullifiers with `onChainCreation[i]=false` to actually withdraw value) and assert it does **not** revert with `"Nullifier cannot be reused"`, demonstrating the same real leaves can be spent again.

### Citations

**File:** circuits/MainEVMCircuit.circom (L17-26)
```text
// public params: 
// rootHashHinkal, signedMessageHash, 
// erc20TokenAddresses, amountChanges, outTimeStamp, inNullifiers, outCommitments, 
// calldataHash, message,
// outH1Ax, outH1Ay, H0Ax, H0Ay, outStealthAddress

// private params:
// spendingPublicKey, eddsaSignature, nullifyingPrivateKey, messageSeed
// inAmounts, inH0Ax, inH0Ay, inTimeStamps, inCommitmentSiblings, inCommitmentSiblingSides,
// outAmounts, outPublicKeys, 
```

**File:** circuits/MainEVMCircuit.circom (L133-134)
```text
        // 3) Checking that nullifier is legit
        inNullifiers[i][j] === calcNullifier[i][j].out;
```

**File:** contracts/Hinkal.sol (L136-146)
```text
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

**File:** contracts/Hinkal.sol (L156-159)
```text
            insertNullifiers(
                circomData.inputNullifiers,
                circomData.onChainCreation
            );
```

**File:** contracts/Hinkal.sol (L383-391)
```text
    function _calculateDeltaAmount(
        CircomData calldata circomData,
        uint256 index
    ) private pure returns (int256) {
        return
            circomData.onChainCreation[index]
                ? int256(0)
                : circomData.amountChanges[index];
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
