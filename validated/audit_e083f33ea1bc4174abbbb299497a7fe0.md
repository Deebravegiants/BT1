### Title
`rootHashHinkalIndex` is accepted by `Hinkal.transact` without being bound to the proof or to `calldataHash` — ([File: contracts/Hinkal.sol])

### Summary
`rootHashHinkalIndex` is used by `rootHashExists()` to select which historical root slot to compare `rootHashHinkal` against, but this field is never included in the SNARK public-input vector nor in the calldata integrity hash, breaking the same class of equality the Monero report describes: a value is *used* to authorize/verify a security-relevant step without being cryptographically bound to the data that was actually authenticated.

### Finding Description
`CircomData.rootHashHinkal` is committed inside the circuit's public inputs via `formBasicInput` [1](#0-0) , and both `rootHashHinkal` and `rootHashHinkalIndex` are excluded from `getHashedCalldata1`/`getHashedCalldata2` [2](#0-1) . Only `rootHashHinkal` (the value) is proof-bound; `rootHashHinkalIndex` is a bare, unchecked calldata field.

`Hinkal.transact` calls `rootHashExists(circomData.rootHashHinkal, circomData.rootHashHinkalIndex)` after proof verification [3](#0-2) , and `rootHashExists` uses the index to directly select a slot in the `roots` mapping and compares it to the supplied root: `return _root != 0 && roots[_rootIndex] == _root;` [4](#0-3) .

Because `roots[_rootIndex]` is keyed by insertion order and multiple different Merkle roots are stored across the tree's lifetime, `rootHashHinkalIndex` is not merely a hint — it's the actual selector into storage. The circuit only proves knowledge of a valid Merkle path against *some* root value equal to `rootHashHinkal`; it does not prove which insertion index that root corresponds to on-chain, and the on-chain check does not independently verify that `roots[_rootIndex]` is genuinely the root that was current when the prover's Merkle path was constructed versus merely a root value that happens to match at an attacker-chosen index. Since `roots` only stores 32-byte root values (not tied irreversibly to a specific index by the contract's equality check beyond direct lookup), this is a lookup-integrity gap of the same shape as the Monero issue: the value used for verification (`_rootIndex`) is disconnected from the value that is cryptographically authenticated (`rootHashHinkal`, which is bound to the proof, but not to a specific index).

### Impact Explanation
If root values can repeat or collide across different tree states (e.g., due to how roots are recorded per insertion in `MerkleBase.sol`), an attacker-controlled `rootHashHinkalIndex` selecting an unintended slot could let a prover satisfy `rootHashExists` for a root that is not the one actually relevant to their claimed nullifier/commitment state, potentially enabling proof-root mismatch scenarios. This maps to "proof or nullifier verification bypass" if exploitable end-to-end.

### Likelihood Explanation
Low-to-uncertain: exploitability depends on whether `roots[index]` values can realistically collide or be manipulated to point to an attacker-favorable root while still being consistent with a valid circuit proof for that same root value. I was not able to fully trace `insertNullifiers`/`insertCommitments`/tree insertion code paths within the given iteration budget to confirm whether `_rootIndex` selection can be weaponized in practice (e.g., whether roots can repeat, or whether index bounds checking in `rootHashExists` (`_rootIndex < MINIMUM_INDEX || _rootIndex >= m_index`) sufficiently constrains this).

### Recommendation
Bind `rootHashHinkalIndex` into `calldataHash` (or the public-input vector) so the prover cannot supply an index disconnected from the proven root, closing the same class of gap the Monero `check_spend_proof`/`get_spend_proof` fix addressed by requiring `tx_hash == txid`.

### Proof of Concept
Not constructed — requires confirming whether `roots[]` can hold colliding/reusable values across indices, which needs deeper analysis of the Merkle tree insertion logic (`MerkleBase.sol`'s `insert()` override, not fully available in this pass) than could be completed within the tool-call budget. This finding should be treated as **uncertain/needs further verification** rather than a confirmed exploit.

### Citations

**File:** contracts/CircomDataBuilder.sol (L20-54)
```text
    function getHashedCalldata1(
        CircomData calldata circomData
    ) internal pure returns (uint256) {
        return
            uint256(
                keccak256(
                    abi.encode(
                        circomData.publicSignalCount,
                        circomData.relay,
                        circomData.emporiumMessage,
                        circomData.externalActionData,
                        circomData.slippageValues
                    )
                )
            );
    }

    function getHashedCalldata2(
        CircomData calldata circomData
    ) internal pure returns (uint256) {
        return
            uint256(
                keccak256(
                    abi.encode(
                        circomData.hookData,
                        circomData.encryptedOutputs,
                        circomData.onChainEncryptedOutput,
                        circomData.feeStructure,
                        circomData.onChainCreation,
                        circomData.originalSender,
                        circomData.extraData
                    )
                )
            );
    }
```

**File:** contracts/CircomDataBuilder.sol (L195-195)
```text
        input[index++] = circomData.rootHashHinkal;
```

**File:** contracts/Hinkal.sol (L57-64)
```text
            // Root Hash Validation
            require(
                rootHashExists(
                    circomData.rootHashHinkal,
                    circomData.rootHashHinkalIndex
                ),
                "Hinkal Root Hash is Incorrect"
            );
```

**File:** contracts/MerkleBase.sol (L53-64)
```text
    function rootHashExists(
        uint256 _root,
        uint256 _rootIndex
    ) public view returns (bool) {
        if (m_index == MINIMUM_INDEX) {
            return _root == 0;
        }
        if (_rootIndex < MINIMUM_INDEX || _rootIndex >= m_index) {
            return false;
        }
        return _root != 0 && roots[_rootIndex] == _root;
    }
```
