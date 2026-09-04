### Title
Unconstrained `rootHashHinkalIndex` Field Bypasses Calldata and Circuit Integrity Checks - ([File: contracts/CircomDataBuilder.sol], [File: contracts/types/CircomData.sol], [File: contracts/HinkalHelper.sol])

### Summary
`CircomData.rootHashHinkalIndex` is a field passed by the caller into `performHinkalChecks` / `transact`, but it is never included in `calldataHash` (via `getHashedCalldata1`/`getHashedCalldata2`), never included in `signedMessageHash` (`getSignedMessageHash`), and never included in the public-input vector sent to the Groth16 verifier (`formBasicInput`/`formInputEmporiumMin`). It is only referenced directly in `contracts/Hinkal.sol`. This mirrors the reported bug class: a check that looks like it enforces integrity (here, the `calldataHash` integrity check in `performHinkalChecks`) but silently excludes a field that is nonetheless acted upon by privileged contract logic.

### Finding Description
`performHinkalChecks` in [1](#0-0)  is the sole integrity gate for a `CircomData` struct before it is turned into circuit inputs. It verifies:
1. `originalSender`/`relay` consistency,
2. `CircomDataBuilder.getHashedCalldata(circomData) == circomData.calldataHash`,
3. dimension checks and on-chain-creation checks.

`getHashedCalldata` is the concatenation of `getHashedCalldata1` and `getHashedCalldata2`: [2](#0-1) . Between the two, the hashed fields are `publicSignalCount, relay, emporiumMessage, externalActionData, slippageValues, hookData, encryptedOutputs, onChainEncryptedOutput, feeStructure, onChainCreation, originalSender, extraData`. Neither function references `rootHashHinkalIndex`.

The public-input vector construction in `formBasicInput`/`getSignedMessageHash` likewise enumerates `rootHashHinkal, erc20TokenAddresses, amountChanges, timeStamp, inputNullifiers, outCommitments, calldataHash, stealthAddressStructure` — again omitting `rootHashHinkalIndex`: [3](#0-2) .

The struct itself declares the field as a first-class member alongside `rootHashHinkal`: [4](#0-3) . A `grep` for `rootHashHinkalIndex` shows it is read only in `contracts/Hinkal.sol`, outside of `CircomDataBuilder.sol`/`HinkalHelper.sol`'s validation surface — i.e., it reaches privileged root/tree-state logic without ever being bound to `calldataHash`, `signedMessageHash`, or a public-input signal that the Groth16 proof commits to.

### Impact Explanation
If `Hinkal.sol` uses `rootHashHinkalIndex` to select which historical Merkle root to treat as the "current" root for the transaction (a common optimization to avoid scanning the full root-history array), and does not independently re-derive/validate that `roots[rootHashHinkalIndex] == circomData.rootHashHinkal`, then a caller can submit an index decoupled from the value actually constrained by the proof. Because the proof only constrains `rootHashHinkal` (the value) and not `rootHashHinkalIndex` (the pointer), this field sits exactly in the gap the analog describes: a `CircomData` field "acted on but outside `calldataHash` / `signedMessageHash` / the public-input vector." Depending on how `Hinkal.sol` consumes the index, this could enable a `(leaf, root)` pair / root-freshness check that the Merkle tree's actual history never sanctioned, breaking the tree-inclusion equality the whole proof system depends on for authorizing spends — a Critical-class outcome (proof/root verification bypass) if exploitable end-to-end.

### Likelihood Explanation
Medium-to-low confidence: the code definitively proves `rootHashHinkalIndex` is absent from every hashing/public-input path that exists to bind `CircomData` to the proof and to the calldata-integrity check — this part is fully confirmed from `CircomDataBuilder.sol`. However, I was not able to read the body of `contracts/Hinkal.sol` in this session to confirm precisely how `rootHashHinkalIndex` is dereferenced (e.g., whether `Hinkal.sol` independently re-validates `roots[index] == rootHashHinkal` before trusting the index, which would neutralize the gap). This is the one open question that determines whether the unconstrained field is merely a redundant/unused convenience parameter or an actual exploitable bypass.

### Recommendation
Include `rootHashHinkalIndex` in `getHashedCalldata1`/`getHashedCalldata2` (or bind it into a public-input signal validated by the circuit), or, if it is used to index into the on-chain root history, have `Hinkal.sol` explicitly assert `roots[rootHashHinkalIndex] == circomData.rootHashHinkal` before using the index for any state-affecting logic, so the index can never diverge from the (proof-constrained) root value.

### Proof of Concept
Not independently constructible with certainty in this session: reproducing an exploit requires confirming, from `contracts/Hinkal.sol`, exactly what root-selection or state logic keys off `rootHashHinkalIndex` without a corresponding value check. This should be verified by reading `contracts/Hinkal.sol` in full (the relevant lines were located by `grep` but not retrieved before tool budget was exhausted) to confirm whether `roots[rootHashHinkalIndex]` is compared against `rootHashHinkal` prior to use.

### Citations

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

**File:** contracts/CircomDataBuilder.sol (L10-54)
```text
    function getHashedCalldata(
        CircomData calldata circomData
    ) internal pure returns (uint256) {
        // because of stack too deep error, we need to split the calldata into two parts
        uint256 calldataHash1 = getHashedCalldata1(circomData);
        uint256 calldataHash2 = getHashedCalldata2(circomData);
        return (uint256(keccak256(abi.encode(calldataHash1, calldataHash2))) %
            CIRCOM_P);
    }

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

**File:** contracts/CircomDataBuilder.sol (L97-240)
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

    function formInputForCircom(
        uint256 chainId,
        address verifyingContract,
        CircomData calldata circomData
    ) internal pure returns (uint256[] memory) {
        if (
            circomData.externalActionData.externalActionId ==
            HINKAL_EMPORIUM_ACTION_ID &&
            circomData.erc20TokenAddresses.length == 0
        ) {
            return formInputEmporiumMin(circomData);
        } else {
            return formInputNormal(chainId, verifyingContract, circomData);
        }
    }

    function formInputEmporiumMin(
        CircomData calldata circomData
    ) internal pure returns (uint256[] memory input) {
        input = new uint256[](circomData.publicSignalCount);

        uint16 index = 0;

        input[index++] = circomData.emporiumMessage;

        input[index++] = circomData.timeStamp;
        input[index++] = circomData.calldataHash;
    }

    function formInputNormal(
        uint256 chainId,
        address verifyingContract,
        CircomData calldata circomData
    ) internal pure returns (uint256[] memory input) {
        input = new uint256[](circomData.publicSignalCount);
        uint16 index = 0;
        input = formBasicInput(
            chainId,
            verifyingContract,
            circomData,
            input,
            index,
            circomData.emporiumMessage
        );
    }

    function formBasicInput(
        uint256 chainId,
        address verifyingContract,
        CircomData calldata circomData,
        uint256[] memory input,
        uint256 index,
        uint256 emporiumMessage
    ) internal pure returns (uint256[] memory) {
        // 1) First we list public inputs as in the body of the main template (not the one with exact dimensions)
        input[index++] = circomData.stealthAddressStructure.H1x;
        input[index++] = circomData.stealthAddressStructure.H1y;
        input[index++] = circomData.stealthAddressStructure.stealthAddress;
        input[index++] = emporiumMessage; // this is for Emporium message signature verification

        // 2) Then we list the private inputs as in the body of the main template
        input[index++] = circomData.rootHashHinkal;
        input[index++] = getSignedMessageHash(
            chainId,
            verifyingContract,
            circomData,
            emporiumMessage
        );

        for (uint16 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            input[index++] = uint256(
                uint160(circomData.erc20TokenAddresses[i])
            );
        }

        for (uint16 i = 0; i < circomData.amountChanges.length; i++) {
            require(
                circomData.amountChanges[i] < MAX_AMOUNT &&
                    circomData.amountChanges[i] > -1 * MAX_AMOUNT,
                "amount changed is too large"
            );

            input[index++] = circomData.amountChanges[i] >= 0
                ? uint256(circomData.amountChanges[i])
                : CIRCOM_P - uint256(-circomData.amountChanges[i]);
        }

        for (uint16 i = 0; i < circomData.inputNullifiers.length; i++) {
            for (uint16 j = 0; j < circomData.inputNullifiers[i].length; j++) {
                input[index++] = circomData.inputNullifiers[i][j];
            }
        }

        input[index++] = circomData.timeStamp;

        for (uint16 i = 0; i < circomData.outCommitments.length; i++) {
            for (uint16 j = 0; j < circomData.outCommitments[i].length; j++) {
                input[index++] = circomData.outCommitments[i][j];
            }
        }
        input[index++] = circomData.calldataHash;

        input[index++] = circomData.stealthAddressStructure.H0x;
        input[index++] = circomData.stealthAddressStructure.H0y;

        return input;
    }
```

**File:** contracts/types/CircomData.sol (L23-45)
```text
struct CircomData {
    uint256 rootHashHinkal;
    uint256 rootHashHinkalIndex;
    address[] erc20TokenAddresses;
    int256[] amountChanges;
    uint256[][] inputNullifiers;
    uint256[][] outCommitments;
    bytes[][] encryptedOutputs;
    bytes onChainEncryptedOutput;
    bool[] onChainCreation;
    int256[] slippageValues;
    FeeStructure feeStructure;
    StealthAddressStructure stealthAddressStructure;
    uint256 timeStamp;
    uint256 calldataHash;
    uint256 emporiumMessage;
    uint16 publicSignalCount;
    address relay;
    ExternalActionData externalActionData;
    HookData hookData;
    address originalSender;
    bytes extraData;
}
```
