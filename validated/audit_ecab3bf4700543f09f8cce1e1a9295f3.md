Confirmed: nullifier = `Poseidon(commitment, signature)` where `signature = Poseidon(nullifyingPrivateKey, commitment)` [1](#0-0) [2](#0-1) . Both depend only on the commitment value and the spender's key — never on the leaf's tree position. This is enough to complete the analog.

### Title
On-chain UTXO commitments use attacker-controlled, uniqueness-unenforced timestamps, allowing colliding commitments whose shared nullifier permanently freezes one deposit - (File: `contracts/external-actions/DepositOnChainUtxosExternalAction.sol`)

### Summary
`DepositOnChainUtxosExternalAction` builds on-chain UTXOs whose `timeStamp` field is taken directly from the caller-supplied `circomData.timeStamp` (plus a per-call index), instead of `block.timestamp` as used elsewhere in the codebase (e.g. `ExternalActionSwap.sol`) [3](#0-2) [4](#0-3) [5](#0-4) . The resulting `UTXO` is hashed on-chain into a leaf via `createOnchainCommitment` using `hash4(amount, erc20Address, stealthAddress, timeStamp)`, bypassing ZK verification of the leaf's structure entirely [6](#0-5) . Because nothing on-chain enforces that this timestamp is fresh, monotonic, or unique per depositor/token/amount/stealthAddress, two separate deposits (honest re-use of the same signer-chosen timestamp, or a deliberately crafted one) can produce **identical leaves**. Since the nullifier is `Poseidon(commitment, signature)` and depends only on the commitment value (not tree position) [1](#0-0) , both leaves share the same nullifier. Spending either one marks that nullifier used in `nullifiers` mapping [7](#0-6) , permanently blocking the withdrawal of the twin leaf even though it was separately funded with real ERC20 tokens.

### Finding Description
`DepositOnChainUtxosExternalAction.runAction` decodes `utxoAmounts` from calldata and, for each entry, builds a `UTXO` with `timeStamp: circomData.timeStamp + utxoIndex`, pulling real tokens from `userAddress` via `transferERC20TokenFrom` for the declared `tokenTotal` [8](#0-7) . `circomData.timeStamp` is a plain user-supplied value integrity-checked only via `calldataHash`/`signedMessageHash` (i.e. it is bound to what the *signer* claims, but not to `block.timestamp`, a nonce, or previous usage) [9](#0-8) [10](#0-9) . The equality that should hold — "every value-bearing leaf inserted into the tree must be spendable exactly once, and no two independently-funded deposits should collapse to one spendable slot" — is broken: `Hinkal.transact()` inserts the on-chain commitment straight into the Merkle tree via `insertCommitments` without any circuit constraint tying the leaf's `timeStamp` to freshness or uniqueness [11](#0-10) , and `checkOnchainCreation` only forces `amountChanges[i] == 0` and zero input nullifiers for the onChainCreation branch — it never inspects `circomData.timeStamp` for collision risk [12](#0-11) . If the same depositor (or two depositors coordinating, e.g. via a shared front-end default value, or a script that reuses a fixed timestamp) calls `transact()` twice with identical `erc20TokenAddresses[i]`, identical `stealthAddressStructure`, identical `utxoAmounts[i][j]`, and the same `circomData.timeStamp` (and same `utxoIndex` position within the batch), the two resulting on-chain commitments are byte-for-byte identical. Both get inserted as separate leaves (duplicate leaves are not rejected — `MerkleBase`/`Merkle` have no leaf-uniqueness check) [13](#0-12) , but they share one nullifier. Spending the first consumes that nullifier permanently, freezing the second (fully paid-for) UTXO forever, since any later attempt to prove ownership of the second leaf recomputes the same `inNullifiers[i][j]` value, which the circuit forces to equal the already-used nullifier [14](#0-13) , and `insertNullifiers` will revert with "Nullifier cannot be reused" [15](#0-14) .

### Impact Explanation
This is a permanent freezing of user funds equal to the value of the colliding deposit: real ERC20 tokens are transferred into the Hinkal pool via `transferERC20TokenFrom`, but the resulting shielded UTXO can never be withdrawn once its twin's nullifier is spent. Per the rules, "permanent freezing of user funds" is a Critical-tier impact.

### Likelihood Explanation
Likelihood is not purely theoretical: because `circomData.timeStamp` is entirely off-chain/client-chosen with no enforced monotonicity or uniqueness check on this path (unlike `ExternalActionSwap.sol`'s `block.timestamp` usage), any client library, script, or naive integration that reuses a cached/rounded timestamp value across two deposit calls for the same recipient/token/amount will trigger the collision unintentionally; a malicious actor could also deliberately construct two deposits that collide to grief another depositor sharing a predictable timestamp scheme, or to lock their own funds for insurance/compliance-evasion reasons that later become someone else's problem if UTXOs are transferred pre-spend.

### Recommendation
Derive the on-chain UTXO `timeStamp` from `block.timestamp` (as `ExternalActionSwap.sol` already does) rather than from `circomData.timeStamp`, and/or fold a monotonically increasing nonce (e.g., `m_index` at insertion time) into the leaf hash in `createOnchainCommitment` so that no two on-chain-created commitments can ever collide regardless of caller-chosen input.

### Proof of Concept
1. Attacker/user Alice calls `Hinkal.transact()` with `externalActionData.externalActionId` pointing to `DepositOnChainUtxosExternalAction`, `erc20TokenAddresses = [TOKEN]`, `onChainCreation = [true]`, `circomData.timeStamp = T`, and `externalActionMetadata` encoding `utxoAmounts = [[100]]`. This transfers 100 `TOKEN` from Alice and inserts leaf `L1 = hash4(100, TOKEN, stealthAddress, T)`.
2. Alice repeats the exact same call a second time (same `stealthAddressStructure`, same `T`, same amount) — a second 100 `TOKEN` is transferred, and leaf `L2 = hash4(100, TOKEN, stealthAddress, T)` is inserted, identical to `L1`.
3. Alice later spends `L1` in a normal `transact()` call, using a valid Merkle path to `L1` in `inCommitmentSiblings`. The circuit computes `nullifier = NullifierCalculator(commitment=L1, signature=Signature(nullifyingPrivateKey, L1))` [1](#0-0) , and `insertNullifiers` marks it used [7](#0-6) .
4. Alice attempts to spend `L2` (same amount/token/stealthAddress/timestamp) via a Merkle path to `L2`. The circuit recomputes the identical nullifier (commitment and signature are the same as for `L1`), and `insertNullifiers` reverts with `"Nullifier cannot be reused"`, permanently freezing the second 100 `TOKEN` deposit.

### Citations

**File:** circuits/NullifierCalculator.circom (L6-18)
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

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L10-13)
```text
/// @title DepositOnChainUtxosExternalAction
/// @notice Deposits tokens into Hinkal and creates on-chain UTXOs whose commitments
/// are fully determined by the caller, because their timestamps come from
/// circomData.timeStamp rather than from the block.
```

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L55-82)
```text
            address tokenAddress = circomData.erc20TokenAddresses[i];
            uint256 tokenTotal = 0;

            for (uint256 j = 0; j < utxoAmounts[i].length; j++) {
                uint256 amount = utxoAmounts[i][j];
                require(
                    amount > 0,
                    "DepositOnChainUtxosExternalAction: UTXO amount must be positive"
                );
                tokenTotal += amount;

                utxoSet[utxoIndex] = UTXO({
                    amount: amount,
                    erc20Address: tokenAddress,
                    stealthAddressStructure: circomData.stealthAddressStructure,
                    timeStamp: circomData.timeStamp + utxoIndex
                });
                utxoIndex++;
            }

            if (tokenAddress != address(0) && tokenTotal > 0) {
                transferERC20TokenFrom(
                    tokenAddress,
                    userAddress,
                    msg.sender,
                    tokenTotal
                );
            }
```

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L95-101)
```text
        utxoSet = new UTXO[](1);
        utxoSet[0] = UTXO({
            amount: amountToSendToHinkal,
            erc20Address: outputToken,
            stealthAddressStructure: circomData.stealthAddressStructure,
            timeStamp: block.timestamp
        });
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

**File:** contracts/HinkalHelper.sol (L208-236)
```text
    function performHinkalChecks(
        CircomData calldata circomData,
        Dimensions calldata dimensions,
        address sender
    ) external view returns (uint256[] memory) {
        require(
            (circomData.originalSender == address(0) &&
                circomData.relay != address(0)) ||
                (circomData.originalSender == sender &&
                    circomData.relay == address(0)),
            "invalid value for originalSender"
        );

        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
        );
        relayerIsValid(circomData.relay);
        dimensionsCheck(circomData, dimensions);
        checkOnchainCreation(circomData);

        return
            CircomDataBuilder.formInputForCircom(
                block.chainid,
                hinkalAddress,
                circomData
            );
    }
```

**File:** contracts/CircomDataBuilder.sol (L97-132)
```text
    function getSignedMessageHash(
        uint256 chainId,
        address verifyingContract,
        CircomData calldata circomData,
        uint256 emporiumMessage
    ) internal pure returns (uint256) {
        // split into two encode calls to avoid "stack too deep"
        uint256 hash1 = uint256(
            keccak256(
                abi.encode(
                    chainId,
                    verifyingContract,
                    circomData.rootHashHinkal,
                    _encodeTokenAddresses(circomData.erc20TokenAddresses),
                    _encodeAmountChanges(circomData.amountChanges),
                    circomData.timeStamp,
                    _flatUint256Matrix(circomData.inputNullifiers),
                    _flatUint256Matrix(circomData.outCommitments),
                    circomData.calldataHash,
                    emporiumMessage
                )
            )
        );
        uint256 hash2 = uint256(
            keccak256(
                abi.encode(
                    circomData.stealthAddressStructure.H1x,
                    circomData.stealthAddressStructure.H1y,
                    circomData.stealthAddressStructure.H0x,
                    circomData.stealthAddressStructure.H0y
                )
            )
        );
        return
            uint256(keccak256(abi.encode(hash1, hash2))) % CIRCOM_P;
    }
```

**File:** contracts/MerkleBase.sol (L47-64)
```text
    function insert(uint256 leaf) internal virtual returns (uint256);

    function getRootHash() public view returns (uint256) {
        return m_index == MINIMUM_INDEX ? 0 : roots[m_index - 1];
    }

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
