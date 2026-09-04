Confirmed: no dedup checks exist in `insertMany`/`sortInPairs`/`insertOne`/`insertTwo` — leaves are inserted purely by position, with no value-uniqueness enforcement.

### Title
Commitment hash lacks index/nonce binding, allowing identical-value duplicate commitments to collide on a single nullifier and permanently freeze one deposit's funds - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`EmporiumUpgradeable.handleOut` builds an output `UTXO` entirely from attacker-controlled `circomData` fields (`stealthAddressStructure`, `timeStamp`) plus a verified `balanceChange`, and `HinkalBase.createOnchainCommitment` hashes `(amount, erc20Address, stealthAddress, timeStamp)` with no tree-index or nonce salt. The circuit's nullifier (`NullifierCalculator`/`Signature`) is derived purely from `(commitment, nullifyingPrivateKey)`, independent of the Merkle leaf's index/path. Two separate Emporium calls that produce identical `(amount, token, stealthAddress, timeStamp)` yield two leaves with the same commitment value at different tree indices but the exact same future nullifier, so spending one permanently blocks spending the other.

### Finding Description
The claimed broken equality is: "one value-bearing leaf == one nullifier ever accepted for it" is violated because two *distinct* leaves (different Merkle indices) can share the same nullifier value.

Exploit path:
1. `EmporiumUpgradeable.handleOut` (lines 162-184) constructs the output UTXO as `UTXO(balanceChange, erc20TokenAddresses[i], circomData.stealthAddressStructure, circomData.timeStamp)`. Both `stealthAddressStructure` and `timeStamp` are fully attacker-supplied via `CircomData` [1](#0-0) , and there is no on-chain check binding `circomData.timeStamp` to `block.timestamp` for the Emporium action (unlike `ExternalActionSwap`, which does enforce `block.timestamp <= circomData.timeStamp + SWAP_DEADLINE_WINDOW`) [2](#0-1) .
2. `HinkalBase.createOnchainCommitment` computes `commitment = hash4(amount, erc20Address, stealthAddress, timeStamp)` with no salt/index/nonce [3](#0-2) .
3. `insertCommitments`/`insertMany` append leaves purely by position (`m_index += leaves.length`), with no duplicate-value check [4](#0-3) .
4. On the circuit side, the nullifier is `NullifierCalculator.out = Poseidon(commitment, signature) * (1 - IsZero(commitment))` where `signature = Poseidon(nullifyingPrivateKey, commitment)` [5](#0-4) [6](#0-5) . Neither depends on the Merkle path/index — only `MerkleRootCalculator` uses the siblings/sides to prove inclusion, but that output is not fed into nullifier derivation [7](#0-6) .
5. `HinkalBase.insertNullifiers` enforces global uniqueness only on the nullifier value: `require(!nullifiers[N], "Nullifier cannot be reused")` [8](#0-7) .

Attacker's exact call sequence: two separate `transact` calls routed through the registered Emporium external action, each with a distinct `emporiumMessage` (so `usedMessages` in `verifyWallet` doesn't block replay) [9](#0-8) , but identical `circomData.timeStamp`, identical `stealthAddressStructure`, and ops engineered so `balanceChange` for `erc20TokenAddresses[i]` equals the same `X` both times. Both deposits pass `balanceDif`/slippage checks in `Hinkal.sol` (lines 97-147) and get inserted as two leaves with an identical commitment value at two different tree indices.

Existing guards (`performHinkalChecks`, `dimensionsCheck`, `checkOnchainCreation`, `rootHashExists`, slippage/balance requires) validate structural consistency and balance-preservation per transaction but do none of the following: (a) enforce uniqueness/monotonicity of `circomData.timeStamp` for Emporium, (b) enforce commitment uniqueness at insertion, or (c) bind the nullifier to leaf index. None of them prevent the collision.

### Impact Explanation
The second, genuinely-verified (`balanceDif`-checked) deposit of `X` tokens becomes permanently unspendable: once the shared nullifier `N` is consumed by spending the first leaf, any attempt to spend the second leaf (same commitment, same derived `N`) reverts forever with "Nullifier cannot be reused." This is a permanent freezing of real, once-verified user funds caused by a protocol architecture gap (commitment scheme lacking index/nonce binding + nullifier scheme lacking index binding), matching the Critical "permanent freezing of user funds" category. It is repeatable for any token/amount/stealth-address/timestamp combination an attacker (or an unwitting legitimate user reusing a fixed timestamp/session id and depositing the same amount twice) chooses to collide.

### Likelihood Explanation
No privileged role is required — any EOA that can call `transact` through the registered Emporium external action and control `circomData` fields can trigger this. Preconditions are trivial: reuse the same `timeStamp` and `stealthAddressStructure`, and engineer two calls whose resulting `balanceChange` is identical (e.g., depositing/withdrawing the same fixed amount through a controlled endpoint twice). Cost is just two ordinary transaction fees; feasibility is high since none of the required fields are contract-enforced to be unique or time-bound for this action.

### Recommendation
Bind commitment uniqueness to the Merkle insertion position or a per-deposit nonce (e.g., include the assigned leaf index, a monotonic on-chain counter, or a fresh random salt in the `hash4` preimage), and correspondingly update the nullifier circuit to derive from a value that is unique per leaf even when `(amount, token, stealthAddress, timeStamp)` repeat. Alternatively, enforce `circomData.timeStamp == block.timestamp` (or a strictly increasing per-user counter) for on-chain-created commitments so duplicate preimages cannot occur, and/or add an explicit on-chain check rejecting insertion of a commitment value that already exists in `nullifiers`-adjacent tracking (e.g. a "seen commitments" set) before calling `insertMany`.

### Proof of Concept
Foundry/Hardhat test plan:
1. Deploy `Hinkal`, `HinkalHelper`, and register `EmporiumUpgradeable` as an external action.
2. Craft `EmporiumStack`/`EmporiumOperation` ops (e.g., a controlled `endpoint` contract) so that two separate `transact` calls each produce `balanceChange == X` for `erc20TokenAddresses[0]`.
3. Call `transact` #1 with `circomData.timeStamp = T`, `circomData.stealthAddressStructure = S`, distinct `emporiumMessage1`; record `commitment1` emitted via `NewCommitment` and its leaf index `idx1`.
4. Call `transact` #2 with the same `T`, `S`, `X`, distinct `emporiumMessage2`; assert emitted `commitment2 == commitment1` and `idx2 != idx1` — this is the equality-violation checkpoint (same commitment value, different index).
5. Generate a valid spend proof for `commitment1` (opening at `idx1`, deriving nullifier `N` off-chain using snarkjs with the real circuit) and call `transact` to spend it; assert `nullifiers[N] == true` after.
6. Generate a spend proof for `commitment2` (opening at `idx2`, same underlying commitment/private key) and call `transact`; assert it reverts with `"Nullifier cannot be reused"`.
7. Assert the on-chain token balance shows both deposits' `X` amounts were received by Hinkal (via `balanceDif` checks passing twice), but only one nullifier-backed withdrawal ever succeeds — proving the second deposit's value is permanently stranded.

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-316)
```text
    function verifyWallet(
        EmporiumStack memory stack,
        CircomData calldata circomData
    ) internal {
        EmporiumStorageVars storage $ = _getEmporiumStorage();

        if ($.usedMessages[circomData.emporiumMessage]) {
            revert UsedMessage();
        }

        $.usedMessages[circomData.emporiumMessage] = true;

        if (stack.signerAddress == address(0)) {
            return;
        }
```

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L58-60)
```text
        require(
            block.timestamp <= circomData.timeStamp + SWAP_DEADLINE_WINDOW,
            "swap expired"
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

**File:** contracts/Merkle.sol (L37-50)
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

**File:** circuits/MainEVMCircuit.circom (L124-148)
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
```
