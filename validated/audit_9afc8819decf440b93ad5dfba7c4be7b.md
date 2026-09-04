### Title
MIN-path Emporium `runAction` calls with `signerAddress == address(0)` carry no chain-binding field, enabling identical-proof replay across chains - ([File: contracts/CircomDataBuilder.sol], [File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
When `formInputForCircom` routes an Emporium transaction to `formInputEmporiumMin` (i.e. `externalActionData.externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0`), the circuit's public-input vector contains only `emporiumMessage`, `timeStamp`, and `calldataHash` — none of which incorporate `chainId` or the verifying contract address. When the accompanying `EmporiumStack.signerAddress` is `address(0)`, `verifyWallet` returns before computing the `_hashTypedDataV4` domain-bound hash, so the EIP-712 domain check (the only other candidate chain-binding mechanism) is also skipped entirely. The result is that a fully valid `circomData` + proof accepted on chain A contains no field that must differ to be re-accepted on chain B.

### Finding Description
The equality being broken: **for the MIN path with `signerAddress == 0`, `inputForCircom(circomData, chainA) == inputForCircom(circomData, chainB)` for the SNARK proof, AND `verifyWallet` performs zero additional binding** — i.e. no field anywhere in the accepted state differs between chain A and chain B.

Trace:
- `formInputForCircom` dispatches to `formInputEmporiumMin` for Emporium-min transactions: [1](#0-0) 
- `formInputEmporiumMin` builds only 3 public signals — `emporiumMessage`, `timeStamp`, `calldataHash` — and never touches the `chainId`/`verifyingContract` parameters that `performHinkalChecks` passes in: [2](#0-1) 
- Contrast with `formInputNormal`/`formBasicInput`, which embed `chainId` and `verifyingContract` into `getSignedMessageHash`, and which is the only place `chainId` is bound into a public/private circuit signal: [3](#0-2) 
- `HinkalHelper.performHinkalChecks` always passes `block.chainid`, but this is silently dropped by the MIN path: [4](#0-3) 
- `getHashedCalldata` (which produces `circomData.calldataHash`, integrity-checked against the same value) is likewise computed purely from `circomData` fields (`relay`, `emporiumMessage`, `externalActionData`, `slippageValues`, `hookData`, `encryptedOutputs`, `feeStructure`, `onChainCreation`, `originalSender`, `extraData`) — no `chainid`, no contract address: [5](#0-4) 
- The MIN circuit itself (`MainEVMCircuitMin`) only constrains `outTimeStamp`, `calldataHash` as public, and `messageSeed` as private, with `message <== Poseidon(1)([messageSeed])` — no chain-related signal exists to constrain: [6](#0-5) 
- `verifyWallet` marks `usedMessages[circomData.emporiumMessage] = true` and then, for `signerAddress == address(0)`, returns immediately — skipping the `_hashTypedDataV4` EIP-712 domain hash (the only mechanism binding `block.chainid` + `address(this)`) entirely: [7](#0-6) 
- `usedMessages` is per-contract storage under an ERC-7201 slot in `EmporiumStorage` — a fresh/independent deployment on a different chain (even at the identical address via CREATE2) has an independent, initially-empty mapping, so the same `emporiumMessage` is not yet "used" there: [8](#0-7) 

Root cause: the MIN-path public-input formula and the calldata-hash formula omit any chain/contract-identity field, and the fallback chain-binding mechanism (`verifyWallet`'s EIP-712 domain) is unconditionally bypassed when `signerAddress == address(0)`.

Exploit flow: an unprivileged attacker calls `transact()` on chain A with `circomData.originalSender = msg.sender`, `circomData.relay = address(0)` (no relay privilege needed), `erc20TokenAddresses.length == 0` (forcing MIN path), and `EmporiumStack.signerAddress = address(0)` (forcing CASE 2 stateless op execution in `runAction`). They set `rootHashHinkalIndex` to the tree's initial/empty root (a value identical across all freshly deployed instances that have not yet accepted deposits) so `rootHashExists` passes without needing any real deposit. They generate a valid MIN-circuit proof locally for arbitrary `emporiumMessage`/`timeStamp`/`calldataHash` and craft `stack.ops` with an arbitrary `endpoint`/`callData`/`value`. This succeeds on chain A. The attacker then submits the byte-identical `(a, b, c, dimensions, circomData)` to an identically-addressed `Hinkal`/`Emporium` deployment on chain B (e.g., a CREATE2-based multichain deployment, common for this kind of protocol). `performHinkalChecks`, `verifyProof`, `rootHashExists`, and `verifyWallet` all pass again on chain B because none of them depend on `block.chainid` or `address(this)` for this code path, and `usedMessages` on chain B is independent storage.

### Impact Explanation
This is a proof/verification bypass of chain-identity binding: an action (arbitrary `op.endpoint.call{value: op.value}(op.callData)`, plus relay-fee payment logic in `payRelayFees`) that the prover/relay only authorized for chain A is replayed and executed a second time on chain B without any new authorization, moving/spending protocol-controlled ETH/token balance and/or invoking arbitrary external calls that were never separately proven for chain B. This matches the "Critical — proof or nullifier verification bypass / executing calls... a prover never authorised" category. It is repeatable for every MIN-path, no-wallet-signature Emporium transaction and across every chain where the contracts are deployed at the same address.

### Likelihood Explanation
Preconditions: (1) `erc20TokenAddresses.length == 0` to force the MIN path — fully attacker-controlled; (2) `EmporiumStack.signerAddress == address(0)` — fully attacker-controlled, decoded from attacker-supplied `externalActionMetadata`; (3) the same contract address deployed on ≥2 chains (a standard deployment pattern via CREATE2/deterministic deployers, common for multichain protocols) with an empty/initial Merkle root reachable without funds. All of these are within reach of an ordinary EOA who can generate their own proofs and deploy nothing more than calling `transact()` on both chains — no privileged role, no victim key material, no relayer whitelist membership required.

### Recommendation
Bind `block.chainid` and `address(this)` into the MIN-path public inputs (e.g., fold them into `formInputEmporiumMin`'s `calldataHash`/`emporiumMessage` derivation the same way `formBasicInput` does via `getSignedMessageHash`), and/or remove the unconditional early return in `verifyWallet` so that a chain/contract-bound hash (even a non-signature commitment) is always computed and constrained regardless of `signerAddress`. At minimum, incorporate `block.chainid` and `address(this)` into `getHashedCalldata`/`calldataHash` so the calldata-hash integrity check in `HinkalHelper.performHinkalChecks` inherently differs per chain.

### Proof of Concept
Foundry fork/multi-chain test plan:
1. Deploy `Hinkal` + `EmporiumUpgradeable` (or reuse two forked networks assumed to have identical bytecode/address, e.g. via `vm.createSelectFork`) representing chain A (`block.chainid = X`) and chain B (`block.chainid = Y`), both fresh (empty Merkle tree, same initial root).
2. As an attacker EOA, build `circomData` with `erc20TokenAddresses = []`, `originalSender = attacker`, `relay = address(0)`, `rootHashHinkalIndex` = initial root index, and `externalActionMetadata` decoding to `EmporiumStack{signerAddress: address(0), ops: [{endpoint: targetContract, invokeWallet: false, value: 0, callData: someCall}], ...}`.
3. Generate a valid `MainEVMCircuitMin` proof locally for chosen `emporiumMessage`, `timeStamp`, `calldataHash` (computed via `getHashedCalldata` off-chain, matching `CircomDataBuilder.getHashedCalldata`).
4. Call `Hinkal.transact(a, b, c, dimensions, circomData)` on chain A fork — assert success, assert `targetContract` state changed once, assert `EmporiumStorage.usedMessages[emporiumMessage] == true` on chain A instance.
5. Call `Hinkal.transact(a, b, c, dimensions, circomData)` with byte-identical arguments on chain B fork — assert it **also succeeds** (no revert from `verifyProof`, `rootHashExists`, `performHinkalChecks`, or `verifyWallet`), and `targetContract` state changes a second time, proving the identical proof/circomData was accepted on a different `block.chainid` with no field forced to differ. Compare both sides of the equality: `inputForCircom(chainA) == inputForCircom(chainB)` (assert equal arrays) and confirm `verifyWallet` never invoked `_hashTypedDataV4` on either chain (e.g., via event/log or by checking domain separator doesn't factor into acceptance).

### Citations

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

**File:** contracts/CircomDataBuilder.sol (L134-148)
```text
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
```

**File:** contracts/CircomDataBuilder.sol (L150-161)
```text
    function formInputEmporiumMin(
        CircomData calldata circomData
    ) internal pure returns (uint256[] memory input) {
        input = new uint256[](circomData.publicSignalCount);

        uint16 index = 0;

        input[index++] = circomData.emporiumMessage;

        input[index++] = circomData.timeStamp;
        input[index++] = circomData.calldataHash;
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

**File:** circuits/MainEVMCircuitMin.circom (L1-18)
```text

pragma circom 2.1.6;

include "../../node_modules/circomlib/circuits/poseidon.circom";

template MainEVMCircuitMin() {
  // Public inputs:
  signal input outTimeStamp;
  signal input calldataHash;

  // Private inputs:
  signal input messageSeed;

  // outputs:
  signal output message;

  message <== Poseidon(1)([messageSeed]);
}
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-317)
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumStorage.sol (L1-26)
```text
// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.17;

import {IHinkalHelper} from "../../../types/IHinkalHelper.sol";

contract EmporiumStorage {
    /// @custom:storage-location erc7201:hinkal.storage.Emporium
    struct EmporiumStorageVars {
        IHinkalHelper _hinkalHelper; // Hinkal Helper may change implementation
        mapping(uint256 => bool) usedMessages;
    }

    // keccak256(abi.encode(uint256(keccak256("hinkal.storage.Emporium")) - 1)) & ~bytes32(uint256(0xff))
    bytes32 private constant EmporiumStorageLocation =
        0xf10f423c12af70b7aa31f6f1bd94310f38d85adab8d26b5c90b7f07c98bf0800;

    function _getEmporiumStorage()
        internal
        pure
        returns (EmporiumStorageVars storage $)
    {
        assembly {
            $.slot := EmporiumStorageLocation
        }
    }
}
```
