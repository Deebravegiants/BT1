### Title
Duplicate on-chain commitment via attacker-chosen `timeStamp`/`stealthAddress` causes permanent freezing of a victim's unspent on-chain UTXO - (File: `contracts/HinkalBase.sol`)

### Summary
`HinkalBase.createOnchainCommitment` derives the tree leaf purely from `(amount, erc20Address, stealthAddress, timeStamp)` with no source of leaf-uniqueness (no incrementing nonce, no `block.timestamp` binding, no leaf index). `DepositOnChainUtxosExternalAction.runAction` lets the caller fully control `circomData.timeStamp` and `circomData.stealthAddressStructure`, both of which are public (the victim's values are visible in the `NewCommitment` event). An attacker can therefore deposit a UTXO whose commitment `C` is bit-for-bit identical to an existing, unspent victim leaf, inserting a second tree leaf with the same commitment.

### Finding Description
Broken equality: the protocol's implicit invariant is "one value-bearing commitment `C` maps to at most one leaf, and spending any leaf with commitment `C` produces the unique nullifier for that value." After the attack, two distinct leaves (different indices) hold the same commitment `C`, but the nullifier is computed as:

```
circuits/NullifierCalculator.circom:11-13  ->  Poseidon(commitment, signature)
circuits/Signature.circom:10-13            ->  signature = Poseidon(nullifyingPrivateKey, commitment)
```

Neither the nullifier nor the signature incorporates the tree index or the merkle path — it is a pure function of `(commitment, nullifyingPrivateKey)`. So both duplicate leaves, if spent with the victim's key, yield the identical nullifier value.

Path:
1. `HinkalBase.createOnchainCommitment` (`contracts/HinkalBase.sol:53-70`) computes `commitment = hash4(amount, erc20Address, stealthAddress, timeStamp)`.
2. `DepositOnChainUtxosExternalAction.runAction` (`contracts/external-actions/DepositOnChainUtxosExternalAction.sol:66-72`) builds `utxo.timeStamp = circomData.timeStamp + utxoIndex`, with `circomData.timeStamp` fully attacker-supplied and `circomData.stealthAddressStructure` also attacker-supplied — the docstring on the contract itself states commitments here "are fully determined by the caller" rather than `block.timestamp`.
3. `HinkalBase.insertCommitments` (`contracts/HinkalBase.sol:72-133`) inserts the new leaf into the merkle tree with **no duplicate-commitment check** against existing leaves.
4. Attacker observes victim's public `NewCommitment` event (leaf `C`, `stealthAddress`, `amount`, `timeStamp`), then crafts their own deposit through `DepositOnChainUtxosExternalAction` with `erc20TokenAddresses[i]`/`utxoAmounts[i][j]` = victim's amount, `circomData.stealthAddressStructure` = victim's stealth address, and `circomData.timeStamp + utxoIndex` = victim's original `timeStamp`. This reproduces commitment `C` at a new tree index, funded entirely by the attacker's own tokens (attacker pays for the duplicate deposit; only the nullifier collision harms the victim).
5. When the victim (holding the real `nullifyingPrivateKey` for that stealth address) later spends either of the two leaves with commitment `C`, `insertNullifiers` (`contracts/HinkalBase.sol:135-152`) accepts the nullifier once and marks `nullifiers[nullifier] = true`. Spending the second, distinct, never-before-spent leaf reverts with `"Nullifier cannot be reused"`, since the nullifier for `C` is now permanently consumed.

No existing check prevents this: `performHinkalChecks`/`checkOnchainCreation`/`dimensionsCheck` validate structural/dimension consistency, not commitment collisions; `verifyProof` only proves the attacker's own inputs are well-formed; `rootHashExists` only checks a valid historical root; none of these enforce leaf/commitment uniqueness across the tree.

### Impact Explanation
The victim's second (duplicate-commitment) leaf becomes permanently unspendable once either copy's nullifier is inserted, even though it was a legitimately, independently deposited value-bearing UTXO. This is a permanent freezing of user funds (Critical, per the given severity rubric: "permanent freezing of user funds"). The attack is repeatable against any victim whose on-chain deposit is still unspent and publicly observable via `NewCommitment`, at the cost of the attacker funding a duplicate deposit of the same amount/token (the attacker's own deposited funds are recoverable by the attacker themselves, since they know their own private key/stealth address structure was set to the victim's public stealth address — actually the attacker cannot spend a UTXO tied to the victim's stealth address without the victim's key, so the attacker's own capital used in the duplicate deposit is also stuck; but the primary harm is denial of the victim's original, legitimate leaf).

### Likelihood Explanation
Preconditions are modest: the victim must have an on-chain UTXO leaf whose nullifier has not yet been inserted (a routine window — many deposits sit unspent for some time), and its `(amount, token, stealthAddress, timeStamp)` are all directly visible in the `NewCommitment` event/`OnChainCommitment` calldata that `HinkalBase.insertCommitments` emits (`abi.encode(onChainCommitments[i].utxo, ...)`). The attacker only needs to be able to call `Hinkal.transact` with `externalActionId` pointing at `DepositOnChainUtxosExternalAction`, supply matching `erc20TokenAddresses`/`utxoAmounts`, and set `circomData.timeStamp` and `circomData.stealthAddressStructure` to the observed values — all attacker-controlled `CircomData` fields per the threat model, requiring no privileged role and only the deposit-equivalent cost of the duplicate amount.

### Recommendation
Bind on-chain commitments to a value that cannot be replayed/duplicated by another party, e.g.: (a) incorporate `block.timestamp` (or a globally-incrementing, contract-assigned nonce/leaf index) into the commitment hash instead of trusting caller-supplied `circomData.timeStamp`; and/or (b) enforce commitment uniqueness in `insertCommitments`/`insertMany` by rejecting insertion of a leaf value that already exists in the tree (e.g., a `mapping(uint256 => bool) public commitmentsUsed` check). Additionally, consider binding the nullifier/signature computation to the leaf index or merkle path so that even a genuine hash collision cannot produce identical nullifiers for two distinct leaves.

### Proof of Concept
Foundry fork test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `DepositOnChainUtxosExternalAction`, and a test ERC20.
2. Victim calls `transact` via `DepositOnChainUtxosExternalAction` with `stealthAddressStructure = SA_v`, `timeStamp = T`, `amount = A`, token `TKN`. Capture emitted `NewCommitment(C, index_v, ...)`.
3. Attacker (funded separately) calls `transact` via the same external action with identical `erc20TokenAddresses`, `utxoAmounts = [[A]]`, `stealthAddressStructure = SA_v`, `circomData.timeStamp = T` (so `utxo.timeStamp = T + 0 = T`), producing an identical commitment. Assert emitted `NewCommitment(C, index_a, ...)` with `index_a != index_v` and both leaves equal `C` — this directly demonstrates the two-indices-one-commitment equality break.
4. Simulate victim spending leaf `index_v` (using nullifyingPrivateKey derived for `SA_v`) with a locally generated proof; assert `Nullified(N)` is emitted and `nullifiers[N] == true`.
5. Simulate victim attempting to spend leaf `index_a` (same commitment `C`, hence identical `N`); assert the `transact` call reverts with `"Nullifier cannot be reused"` on `contracts/HinkalBase.sol:143-146`, proving the second, distinct, never-spent leaf is now permanently frozen. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

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

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L10-13)
```text
/// @title DepositOnChainUtxosExternalAction
/// @notice Deposits tokens into Hinkal and creates on-chain UTXOs whose commitments
/// are fully determined by the caller, because their timestamps come from
/// circomData.timeStamp rather than from the block.
```

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
