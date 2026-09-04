### Title
Nullifier is bound only to (commitment, nullifyingPrivateKey) with no leaf-index/tree binding, so an attacker-fundable duplicate on-chain commitment permanently freezes one of two identical-preimage UTXOs - (File: circuits/NullifierCalculator.circom, contracts/HinkalBase.sol)

### Summary
`NullifierCalculator` derives a nullifier purely from `Poseidon(commitment, signature)`, and `commitment = Poseidon(amount, erc20TokenAddress, stealthAddress, timeStamp)` with no leaf index, tree root, chain id, or contract address mixed in. Because `Hinkal.prooflessDeposit` lets any unprivileged address mint an on-chain commitment with fully attacker-chosen `amount`, `erc20Address`, and `stealthAddressStructure` (only `timeStamp = block.timestamp` is outside attacker control), an attacker who lands a `prooflessDeposit` call in the same block as a victim's deposit (front-run/same-block bundling, trivially reproducible by an attacker calling it twice against themselves in one tx) creates a second leaf with an *identical* commitment. Both leaves resolve to the identical nullifier, so `HinkalBase.insertNullifiers`'s single global `nullifiers` map permanently blocks the second spend — one full `amount` of real value becomes permanently unredeemable.

### Finding Description
The claimed invariant is: **one value-bearing leaf ⇒ one nullifier ever recorded for it**. This is broken because the nullifier equality checked on-chain never includes the leaf's tree position:

- Commitment (both on-chain and in-circuit) is `Poseidon(amount, erc20TokenAddress, stealthAddress, timeStamp)`: [1](#0-0) [2](#0-1) 

- Nullifier is `Poseidon(commitment, Poseidon(nullifyingPrivateKey, commitment))`, with **no** leaf index, merkle root, chain id, or verifying contract folded in: [3](#0-2) [4](#0-3) 

- The circuit only re-derives and equality-checks the nullifier against the same commitment/private-key pair, and separately checks Merkle inclusion of that commitment against *any* path in the tree — it never ties the nullifier to *which* leaf was proven: [5](#0-4) 

- On-chain, nullifiers are tracked in one global boolean map with no domain separation by leaf, chain, or deployment: [6](#0-5) [7](#0-6) 

- `prooflessDeposit` is callable by any unprivileged address and lets the caller fully choose `amount`, `erc20Addresses`, and `stealthAddressStructures`; only `timeStamp` is fixed to `block.timestamp` at execution: [8](#0-7) [9](#0-8) 

- All fields needed to replicate a target commitment (`amount`, `erc20Address`, `stealthAddressStructure`, and the raw `utxo` including `timeStamp`) are emitted in cleartext in `NewCommitment`, so an attacker can precisely target a specific victim deposit and only needs to land their own `prooflessDeposit` call in the *same block* (same `block.timestamp`) to reproduce an identical leaf: [10](#0-9) 

Exploit flow: attacker observes (or replays in the same transaction against themselves) a target `(amount, erc20Address, stealthAddressStructure, block.timestamp)` and calls `prooflessDeposit` with matching parameters, paying `amount` in tokens themselves. This inserts a second leaf whose commitment is bit-for-bit identical to the target leaf's commitment. Both leaves are indistinguishable to the recipient's wallet except by tree index; whichever is spent first via `Hinkal.transact` sets the shared nullifier in `nullifiers`; the second spend attempt (valid Merkle proof, valid signature, valid ZK proof) is rejected by `insertNullifiers`'s `require(!nullifiers[...])` even though it references a distinct, genuinely value-backed leaf: [11](#0-10) 

None of the existing guards (`rootHashExists`, `verifyProof`, `ForceEqualIfEnabled` merkle checks, balance-diff requires in `Hinkal.transact`) prevent this, because they all operate on the *value* of the commitment/nullifier, not on tree position — the system has no domain separation to distinguish two leaves that happen to share a preimage.

### Impact Explanation
Whichever of the two identical-commitment leaves is spent second becomes permanently unspendable: its nullifier can never be validly emitted again since the nullifier is a pure deterministic function of `(commitment, nullifyingPrivateKey)` and both leaves share the same commitment. The `amount` backing that stranded leaf is locked in the `Hinkal` contract forever with no recovery path. Since the attacker fully controls which `(amount, erc20Address, stealthAddressStructure)` they replicate and can force same-block inclusion, they can target a specific known victim deposit; because which of the two indistinguishable leaves gets spent first is not attacker-controlled from the victim's side, this creates a real risk that the victim's *own* genuine deposit is the one left permanently frozen. This matches "permanent freezing of user funds" (Critical/High per the given severity table). It is repeatable against any newly observed on-chain deposit, at the cost of the attacker matching the deposit amount.

### Likelihood Explanation
Preconditions: attacker needs to get a `prooflessDeposit` call into the same block as a target deposit with matching `amount`/`erc20Address`/`stealthAddressStructure` (all visible in `NewCommitment`/calldata), or — trivially and without any timing risk — an attacker/user can reproduce this against their own two deposits by invoking `prooflessDeposit` twice within a single attacker-authored transaction (guaranteeing identical `block.timestamp`), proving the collision is deterministic and cheap, not probabilistic. Attacker cost equals the `amount` they must deposit to build the colliding leaf. This is fully reachable by an unprivileged EOA/contract with no special role required.

### Recommendation
Bind the nullifier (or the commitment) to a unique per-leaf domain, e.g. include the Merkle leaf index (or a strictly monotonically increasing on-chain nonce/leaf counter) as an explicit input to `NullifierCalculator`/`OriginalCommitmentCalculator`, or enforce uniqueness of on-chain commitments at insertion time (reject/salt duplicate commitments in `insertCommitments`/`createOnchainCommitment`) so two leaves can never share a preimage, and thus never share a nullifier.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal` + `HinkalHelper` + circuit verifier as in the repo's normal setup.
2. From attacker address, call `Hinkal.prooflessDeposit` twice in the same transaction (via a small helper contract) with identical `erc20Addresses`, `amounts`, and `stealthAddressStructures` (attacker's own stealth address) — asserts both `NewCommitment` events carry the identical `commitment` value (same `hash4(amount, token, stealthAddress, timeStamp)` since both calls share `block.timestamp`).
3. Off-chain, generate two valid Groth16 proofs (locally, via snarkjs) spending each of the two leaves respectively (same `nullifyingPrivateKey`, same commitment, two different Merkle paths/leaf indices).
4. Call `Hinkal.transact` with the first proof: assert success, `nullifiers[N]==true`, funds released.
5. Call `Hinkal.transact` with the second proof: assert `verifyProof` and `rootHashExists` both pass, but the call reverts at `insertNullifiers` with "Nullifier cannot be reused", proving the second leaf's `amount` is permanently frozen despite being a distinct, validly-included, value-bearing leaf.
6. Assert equality-broken pair: `commitment(leafA) == commitment(leafB)` and `nullifier(leafA) == nullifier(leafB)` both hold true, while `leafIndex(leafA) != leafIndex(leafB)`.

### Citations

**File:** contracts/HinkalBase.sol (L23-23)
```text
    mapping(uint256 => bool) public nullifiers;
```

**File:** contracts/HinkalBase.sol (L53-62)
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
```

**File:** contracts/HinkalBase.sol (L122-131)
```text
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

**File:** circuits/OriginalCommitmentCalculator.circom (L6-22)
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

**File:** contracts/Hinkal.sol (L263-295)
```text
    function prooflessDeposit(
        address[] calldata erc20Addresses,
        uint256[] calldata amounts,
        StealthAddressStructure[] calldata stealthAddressStructures,
        bytes[] calldata onChainEncryptedOutputs,
        bool createBlockedUtxos,
        string calldata orderId // unused on-chain; off-chain listeners read it from calldata to match this tx to an order
    ) public payable nonReentrant {
        hinkalHelper.performProoflessDepositChecks(
            erc20Addresses,
            amounts,
            stealthAddressStructures,
            onChainEncryptedOutputs
        );

        (
            TokenWithAmount[] memory uniqueTokens,
            uint256 uniqueCount
        ) = _calcTokenChangesForProoflessDeposit(erc20Addresses, amounts);

        _handleTransfersFromProoflessDeposit(uniqueTokens, uniqueCount);

        _createProoflessDepositCommitments(
            erc20Addresses,
            amounts,
            stealthAddressStructures,
            onChainEncryptedOutputs
        );

        if (createBlockedUtxos) {
            markUtxosAsBlocked();
        }
    }
```

**File:** contracts/Hinkal.sol (L326-354)
```text
    function _createProoflessDepositCommitments(
        address[] calldata erc20Addresses,
        uint256[] calldata amounts,
        StealthAddressStructure[] calldata stealthAddressStructures,
        bytes[] calldata onChainEncryptedOutputs
    ) private {
        uint256 length = erc20Addresses.length;
        OnChainCommitment[]
            memory onChainCommitmentsArray = new OnChainCommitment[](length);

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

        insertCommitments(
            new uint256[][](0), // off-chain commitments are empty
            new bytes[][](0), // off-chain encrypted outputs are empty
            onChainCommitmentsArray,
            new bool[](0) // on-chain creation is empty
        );
    }
```
