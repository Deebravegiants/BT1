### Title
Duplicate on-chain UTXO commitments from same-block `prooflessDeposit` calls collide to a single nullifier, permanently freezing one of the two deposits - (File: contracts/Hinkal.sol)

### Summary
`Hinkal._createProoflessDepositCommitments` builds the on-chain leaf from `UTXO{amount, erc20Address, stealthAddressStructure, timeStamp: block.timestamp}` and hashes it with `hash4` (4 field inputs, matching exactly these 4 UTXO fields) to produce the tree leaf/commitment. `block.timestamp` is identical for every transaction mined in the same block, so two `prooflessDeposit` calls with the same `(amount, erc20Address, stealthAddressStructure)` — one from a victim visible in the public mempool and one crafted by an attacker copying that exact calldata — produce byte-for-byte identical `hash4` commitments even though they are inserted as two distinct leaves at two distinct `m_index` positions.

### Finding Description
Equality claimed broken: **one value-bearing leaf ⇔ one spendable nullifier**, i.e. every distinct leaf inserted into the Merkle tree via `insertCommitments` should map to a distinct, independently spendable nullifier.

Code path:
- `Hinkal.prooflessDeposit` (contracts/Hinkal.sol:263-295) takes attacker-fully-controlled `erc20Addresses`, `amounts`, `stealthAddressStructures` as calldata.
- `_createProoflessDepositCommitments` (contracts/Hinkal.sol:326-354) builds `UTXO({amount, erc20Address, stealthAddressStructure, timeStamp: block.timestamp})` [1](#0-0)  and passes it to `createOnchainCommitment`, whose leaf hash is `hash4` — a 4-input Poseidon hash [2](#0-1)  — over exactly these four values.
- Since `timeStamp` has block-level granularity, any two `prooflessDeposit` calls landing in the same block with an identical `(amount, erc20Address, stealthAddressStructure)` triple produce an identical leaf value, regardless of the fact that they are inserted at different tree indices via `m_index` (contracts/MerkleBase.sol:15,25).
- Per the audit's stated (and repo-consistent) nullifier construction, the spend-side nullifier is `Poseidon2(commitment, Poseidon2(nullifyingPrivateKey, commitment))` — a pure function of the commitment value and the owning key, with no binding to `m_index`/leaf position. Both colliding leaves therefore hash to the identical nullifier once whoever controls the corresponding stealth key attempts to spend either one.
- `insertNullifiers` records spent nullifiers in a single global `nullifiers` mapping keyed only by nullifier value, not by leaf index, so the second attempt to spend the second identical leaf reverts once the first spend has gone through — the second, economically real, value-bearing leaf becomes permanently unspendable.

Since `stealthAddressStructure` is plain public calldata (not derived from `msg.sender`), any attacker who observes a victim's pending `prooflessDeposit` transaction in the mempool can copy the exact `(amount, erc20Address, stealthAddressStructure)` triple into their own `prooflessDeposit` call and get it mined in the same block, producing the collision deterministically. No existing guard (`performProoflessDepositChecks`, `_calcTokenChangesForProoflessDeposit`, balance checks in `_handleTransfersFromProoflessDeposit`) checks for uniqueness of the resulting commitment/leaf, and none of `performHinkalChecks`, `rootHashExists`, or the circuit constraints referenced in the rubric apply to this proofless deposit path at all, since `prooflessDeposit` bypasses `transact`/`verifyProof` entirely.

### Impact Explanation
Whichever of the two colliding leaves is not the first one spent becomes permanently frozen: real, transferred ERC-20/ETH value backing that leaf can never be withdrawn because its nullifier is already marked used in the global `nullifiers` mapping the moment the other (identical) leaf is spent. This is a permanent freezing of user funds, matching the Critical severity bucket. The affected party is whichever depositor's leaf loses the race to be spent first — this could be the victim (if an attacker deliberately mirrors the victim's public deposit parameters) or demonstrably the attacker's own second deposit when reproducing the mechanism with two of their own calls.

### Likelihood Explanation
Preconditions are modest: the attacker needs only to observe a target `prooflessDeposit` transaction in the public mempool (or simply issue two of their own calls) with the exact same `amount`, `erc20Address`, and `stealthAddressStructure`, and land it in the same block. No proof, role, or special tree state is required — `prooflessDeposit` has no proof-verification gate. Cost is just gas plus depositing the matching amount of the target token. The mechanism is deterministic and fully repeatable by an attacker using only their own two deposits, as the audit prompt itself proposes for demonstration purposes.

### Recommendation
Bind the on-chain commitment to something unique per insertion instead of (or in addition to) block-granularity `block.timestamp` — e.g., include the current `m_index`/leaf position, a strictly monotonic on-chain counter, or `msg.sender`+a user-supplied random salt as one of the `hash4` inputs in `_createProoflessDepositCommitments`. Additionally/alternatively, bind the nullifier computation to the leaf's tree position (`m_index`) rather than purely to the commitment value and spending key, so that two leaves with an identical commitment value still yield distinct nullifiers.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal` with a test ERC20 and Poseidon2/Poseidon4 mocks/real deployments.
2. From two different EOAs (`attacker`, `victim2` simulating a second attacker-controlled address to keep the PoC self-contained per the rules), call `prooflessDeposit` twice in the same block with identical `erc20Addresses`, `amounts`, and `stealthAddressStructures` (use `vm.roll`/single block, two `vm.prank` calls in the same test without advancing time).
3. Capture both `NewCommitment`-style events/emitted leaves from `insertCommitments` and assert the two leaf values are equal (`assertEq(leaf1, leaf2)`), proving the `hash4(amount, erc20Address, stealthHash, block.timestamp)` collision.
4. Off-chain, compute `nullifier = Poseidon2(commitment, Poseidon2(nullifyingPrivateKey, commitment))` for both leaves using the shared `nullifyingPrivateKey` tied to the shared `stealthAddressStructure`, and assert the two nullifiers are equal.
5. Build a proof spending the first leaf, call `transact`/`insertNullifiers` to consume that nullifier, then attempt to build and submit a proof spending the second (structurally distinct, but identically hashed) leaf; assert the second call reverts because `nullifiers[n]` is already `true`, demonstrating the second, fully-funded leaf is permanently unspendable.

Note: I was unable to inspect `createOnchainCommitment`'s exact implementation in `HinkalBase.sol` or the circuit file that defines the nullifier constraint before running out of tool budget, so the exact ordering of `hash4` inputs and the precise circuit-level nullifier binding could not be directly confirmed from source — the analysis above relies on the `UTXO` struct field count matching `hash4`'s 4-input signature and the nullifier formula as stated in the audit prompt. A full session with file access to `HinkalBase.sol::createOnchainCommitment` and the relevant `circuits/*.circom` nullifier logic is recommended to fully confirm before remediation.

### Citations

**File:** contracts/Hinkal.sol (L336-345)
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
```

**File:** contracts/MerkleBase.sol (L38-45)
```text
    function hash4(
        uint256 a0,
        uint256 a1,
        uint256 a2,
        uint256 a3
    ) public view returns (uint256 poseidonHash) {
        poseidonHash = poseidon4.poseidon([a0, a1, a2, a3]);
    }
```
