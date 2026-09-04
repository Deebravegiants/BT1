### Title
Duplicate on-chain UTXO leaves via caller-controlled `circomData.timeStamp` permanently brick one of two identical shielded deposits - (File: contracts/external-actions/DepositOnChainUtxosExternalAction.sol)

### Summary
The reported bug's root cause is a derived, caller/state-influenced value (`lastMintDate` built from a count-based offset) that is not scoped correctly per phase, allowing two logically distinct actions to collide and desynchronize an equality check that a legitimate later actor depends on. The closest reachable analog in this repo is the leaf-commitment construction in `DepositOnChainUtxosExternalAction.runAction`, where the per-UTXO timestamp used to build the Merkle leaf is derived from a fully caller-supplied `circomData.timeStamp` plus a call-local index, with no linkage to `block.timestamp` or any global counter. Two independently authorized calls (e.g. the same depositor sending the same amount, token, and stealth address twice) can therefore produce bit-for-bit identical leaves in the Merkle tree.

### Finding Description
`DepositOnChainUtxosExternalAction.runAction` builds every on-chain UTXO's leaf pre-image from `amount`, `erc20Address`, `stealthAddressStructure`, and `timeStamp`: [1](#0-0) 

`timeStamp` here is `circomData.timeStamp + utxoIndex`, where `circomData.timeStamp` is an arbitrary value chosen by the caller/prover (it is simply passed through as a `CircomData` field and folded into `calldataHash`, but never checked against `block.timestamp` or any monotonically-increasing on-chain counter): [2](#0-1) 

The leaf commitment itself is `hash4(amount, erc20Address, stealthAddress, timeStamp)`, computed identically whether created on-chain (via `Hinkal`/`HinkalBase`) or off-chain (via the circuit's `OriginalCommitmentCalculator`), and the spending nullifier is derived purely from `(commitment, signature)` — it carries no dependency on the leaf's tree index: [3](#0-2) [4](#0-3) [5](#0-4) 

Because nothing enforces that `circomData.timeStamp` is unique across separate calls to this action, a user (or the same depositor) can invoke `transact()` twice with identical `amount`, `erc20Address`, `stealthAddressStructure`, and `circomData.timeStamp`. `insertCommitments`/`insertMany` will happily insert the same leaf value at two different tree indices — there is no uniqueness check on leaves before insertion: [6](#0-5) [7](#0-6) 

Both leaves are individually valid (each is a real leaf the tree produced, with its own valid Merkle proof), but they hash to the *same* commitment, hence the *same* nullifier when later spent (`inputNullifiers[i][j] === calcNullifier[i][j].out`, checked in `MainEVMCircuit.circom` line 134, and enforced globally in `HinkalBase.insertNullifiers`): [8](#0-7) 

When the owner of the stealth address spends the first of the two identical UTXOs, its nullifier is marked as used. Any subsequent attempt to spend the second, structurally distinct (different Merkle path) but content-identical UTXO computes the exact same nullifier and is rejected by `require(!nullifiers[...], "Nullifier cannot be reused")`. The second UTXO's value becomes permanently unspendable even though it was a legitimately inserted, backed leaf.

### Impact Explanation
This breaks the "each accepted, funded leaf must be independently spendable" invariant: a value-bearing leaf that the tree legitimately produced becomes permanently frozen because its nullifier collides with an unrelated sibling deposit's nullifier. This matches the in-scope "permanent freezing of user funds" impact class, since the second UTXO's underlying token balance (already pulled into the contract via `transferERC20TokenFrom`) can never be withdrawn by its rightful owner.

### Likelihood Explanation
Reaching `DepositOnChainUtxosExternalAction` requires only a normal `transact()` call routed through this external action (it is registered as an allowed recipient, invoked by the `Hinkal` contract itself, which any unprivileged EOA can trigger with a valid proof/calldata). No admin/relay/owner privilege is required to pick a caller-controlled `circomData.timeStamp` and repeat identical UTXO parameters across two calls; the only requirement is submitting two transactions with matching `(amount, erc20Address, stealthAddressStructure, timeStamp)`, which is entirely under the caller's control. This can occur accidentally (e.g., a wallet/relayer reusing a nonce-like timestamp scheme) or be deliberately triggered by an attacker targeting a victim's known/observed stealth address to grief a specific deposit.

### Recommendation
Do not let leaf uniqueness depend solely on a caller-supplied `timeStamp`. Either (a) derive the per-leaf timestamp component from a strictly monotonic, contract-maintained counter (e.g. `m_index` at time of insertion) rather than trusting `circomData.timeStamp + utxoIndex`, or (b) bind the nullifier calculation to the leaf's tree index/root position rather than only to `(commitment, signature)`, so structurally distinct leaves never share a nullifier even if their content is identical.

### Proof of Concept
1. Attacker/depositor calls `Hinkal.transact()` with `externalActionData.externalAddress = DepositOnChainUtxosExternalAction`, `circomData.timeStamp = T`, and `utxoAmounts[i] = [X]` for token `i`, `stealthAddressStructure = S`.
   - This creates leaf `L1 = hash4(X, token_i, S.stealthAddress, T+0)` at tree index `k1`.
2. The same or a colluding caller repeats step 1 with identical `amount = X`, `erc20TokenAddresses[i]`, `stealthAddressStructure = S`, and `circomData.timeStamp = T` (nothing prevents reuse).
   - This creates leaf `L2 = hash4(X, token_i, S.stealthAddress, T+0) = L1` at a different tree index `k2 ≠ k1`.
3. The owner of stealth address `S` spends the UTXO using the Merkle path for index `k1`. The circuit computes nullifier `N = f(commitment, signature)` and `HinkalBase.insertNullifiers` marks `N` used.
4. The owner attempts to spend the UTXO at index `k2` (same commitment `L1 == L2`, same signature key) — the circuit again derives nullifier `N`, and `require(!nullifiers[N], ...)` reverts, permanently freezing the funds backing the second leaf despite it having a fully valid, independent Merkle inclusion proof.

### Citations

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L66-72)
```text
                utxoSet[utxoIndex] = UTXO({
                    amount: amount,
                    erc20Address: tokenAddress,
                    stealthAddressStructure: circomData.stealthAddressStructure,
                    timeStamp: circomData.timeStamp + utxoIndex
                });
                utxoIndex++;
```

**File:** contracts/types/CircomData.sol (L36-37)
```text
    uint256 timeStamp;
    uint256 calldataHash;
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

**File:** contracts/HinkalBase.sol (L88-106)
```text
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

**File:** circuits/MainEVMCircuit.circom (L124-134)
```text
        // 2) Calculating Nullifier from commitment and signature
        calcSignature[i][j] = Signature();
        calcSignature[i][j].nullifyingPrivateKey <== nullifyingPrivateKey;
        calcSignature[i][j].commitment <== calcCommitment[i][j].out;

        calcNullifier[i][j] = NullifierCalculator();
        calcNullifier[i][j].commitment <== calcCommitment[i][j].out;
        calcNullifier[i][j].signature <== calcSignature[i][j].out;

        // 3) Checking that nullifier is legit
        inNullifiers[i][j] === calcNullifier[i][j].out;
```

**File:** contracts/Merkle.sol (L37-71)
```text
    function insertMany(
        uint256[] memory leaves
    ) internal returns (uint256[] memory insertedIndexes) {
        m_index += leaves.length;
        uint256 newIndex = m_index;
        uint256 currentNodeIndex = newIndex - leaves.length;

        require(m_index <= uint256(2) ** LEVELS, "Tree is full.");

        insertedIndexes = new uint256[](leaves.length);
        for (uint256 i = 0; i < insertedIndexes.length; i++) {
            insertedIndexes[i] = currentNodeIndex + i;
        }

        uint256[][] memory sortedLeaves = sortInPairs(leaves, currentNodeIndex);

        uint256 fullCount = newIndex - MINIMUM_INDEX; // number of inserted leaves
        uint256 twoPower = logarithm2(fullCount); // number of tree levels to be updated, (e.g. if 9 => 4 levels should be updated)

        for (uint256 i = 0; i < sortedLeaves.length; i++) {
            if (sortedLeaves[i].length == 1)
                insertOne(currentNodeIndex++, twoPower, sortedLeaves[i][0]);
            else {
                insertTwo(
                    sortedLeaves[i][0],
                    sortedLeaves[i][1],
                    currentNodeIndex,
                    twoPower
                );
                currentNodeIndex += 2;
            }
        }

        roots[newIndex - 1] = tree[twoPower]; // adding root to roots mapping
    }
```
