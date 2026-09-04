### Title
Chain-independent `calldataHash`/Emporium-min public inputs allow cross-deployment replay of external-action proofs - (File: contracts/CircomDataBuilder.sol)

### Summary
`getHashedCalldata`/`getHashedCalldata1`/`getHashedCalldata2` never mix in `block.chainid` or `hinkalAddress`, and for the zero-token Emporium branch the circuit's entire public-input vector (`formInputEmporiumMin`) is limited to `emporiumMessage, timeStamp, calldataHash` — none of which are chain- or contract-bound. A `circomData`/proof pair valid on one Hinkal deployment therefore also satisfies `performHinkalChecks` and `verifyProof` on any other deployment that shares the same registered `externalActionId`, `Emporium` contract layout, and Merkle root state.

### Finding Description
The broken equality is: **"a proof + `circomData` accepted by deployment A" ⇒ "same proof + `circomData` accepted by deployment B"**, when it should only ever hold for A.

- `getHashedCalldata1`/`getHashedCalldata2` hash only `publicSignalCount, relay, emporiumMessage, externalActionData, slippageValues, hookData, encryptedOutputs, onChainEncryptedOutput, feeStructure, onChainCreation, originalSender, extraData` [1](#0-0) . `chainid`/`hinkalAddress` are absent from this commitment.
- `performHinkalChecks` re-derives `getHashedCalldata(circomData)` and compares it to `circomData.calldataHash` — a check that is identical on every chain because none of its inputs are chain-scoped [2](#0-1) .
- The general path (`formInputNormal`/`formBasicInput`) *does* fold `chainid` and `hinkalAddress` into the public input vector, via `getSignedMessageHash(chainId, verifyingContract, ...)` [3](#0-2) [4](#0-3) , so a Groth16 proof generated for chain A's public inputs will fail `verifyProof` on chain B (different `signedMessageHash`).
- However, for the special case `externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0`, `formInputForCircom` routes to `formInputEmporiumMin`, whose public-input array is only `[emporiumMessage, timeStamp, calldataHash]` [5](#0-4) . None of these three values are chain- or contract-bound, so the exact same `(a,b,c)` proof verifies against the exact same public-input vector on a second deployment.
- Downstream, `EmporiumUpgradeable.verifyWallet` only enforces a chain/contract-bound EIP-712 signature when `stack.signerAddress != address(0)`; for the "stateless" path (`signerAddress == address(0)`) it merely checks/sets the per-contract `usedMessages[emporiumMessage]` nonce and returns [6](#0-5) . That nonce is deployment-local storage, so it is unset on a second chain and does not block replay.
- The zero-token branch also skips all the balance/slippage invariants in `Hinkal.transact` (the `erc20TokenAddresses` loop is empty), and skips `insertNullifiers`/`insertCommitments` beyond empty arrays, so the only remaining state check is `rootHashExists(circomData.rootHashHinkal, ...)` [7](#0-6) . Since Merkle trees of identical depth/hash/zero-value are deterministic, a genesis (empty-tree) root is identical across every fresh deployment, so this check does not provide chain-binding either.
- Net effect: an attacker who once obtains a valid `(a,b,c, circomData)` for a stateless Emporium operation (`op.endpoint.call{value: op.value}(op.callData)` in `EmporiumUpgradeable.runAction`) can resubmit the identical bytes to `Hinkal.transact` on any other deployment registering the same `externalActionId`, re-triggering the same arbitrary external call against that deployment's `Emporium` contract state/balance.

### Impact Explanation
The replayed call executes `op.endpoint.call{value: op.value}(op.callData)` inside the target chain's `Emporium` contract, against that contract's actual pooled balances/allowances (funds belonging to other users of that deployment), not merely the attacker's own funds. This can move or drain shielded/in-flight funds that the prover never authorized for that specific deployment — matching the Critical category (theft of shielded/in-flight user funds, proof-coverage bypass) since the "authorization" (the ZK proof) was never meant to extend beyond the chain/contract it was generated for. The attack is repeatable against every deployment sharing the `externalActionId`/Emporium bytecode and reachable root state.

### Likelihood Explanation
Preconditions: attacker must be able to produce a valid Emporium-min proof with `erc20TokenAddresses.length == 0` and `stack.signerAddress == address(0)` (stateless ops), a `rootHashHinkal` that also exists on the target chain (trivially true for the genesis root of a freshly deployed/still-empty tree, or any root shared by design), and matching `externalActionId` registration on the target `Hinkal`/`Emporium` pair (realistic for multi-chain-deployed protocols using identical `externalActionMap` wiring). No privileged role is required — this is exactly the unprivileged EOA scenario described (deposit own funds, craft `CircomData`, generate own proof, call `transact` directly). Cost is one proof generation, replayed for free on every additional chain.

### Recommendation
Bind `calldataHash` (and by extension `getHashedCalldata`) to `block.chainid` and `hinkalAddress`, the same way `getSignedMessageHash` already does, so `performHinkalChecks` rejects cross-deployment reuse regardless of which `formInputForCircom` branch is taken. Additionally, include `chainid`/`verifyingContract` inside `formInputEmporiumMin`'s public-input vector so the Groth16 proof itself is bound to the deployment, and require `EmporiumUpgradeable.verifyWallet`'s stateless path to also incorporate a chain/contract-bound value into whatever it treats as "used" (not just a local `usedMessages` nonce).

### Proof of Concept
Hardhat test plan:
1. Deploy two independent `Hinkal`/`HinkalHelper`/`Emporium` stacks (simulating chain A and chain B) with identical `externalActionId` registration and both trees at genesis (or force matching roots).
2. Build one `CircomData` object with `erc20TokenAddresses = []`, `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `emporiumMessage`, `stack.signerAddress = address(0)`, and compute `calldataHash = getHashedCalldata(circomData)` off-chain (via a harness contract exposing the internal function).
3. Assert `getHashedCalldata(circomData)` returns the identical value regardless of which contract instance/chain id is used as caller context (`vm/hardhat` fork with different `block.chainid`, or by calling the harness deployed on both stacks) — this proves the equality claimed.
4. Generate a real Groth16 proof for the `formInputEmporiumMin` public inputs `[emporiumMessage, timeStamp, calldataHash]`.
5. Call `transact` on deployment A: assert success, `EmporiumUpgradeable A.usedMessages[emporiumMessage] == true`.
6. Call `transact` on deployment B with the identical `(a,b,c,dimensions,circomData)`: assert it also succeeds (proof verifies, `performHinkalChecks` passes, `rootHashExists` passes on B's genesis root), and that `op.endpoint.call` executes again on B — demonstrating unauthorized replay across deployments.

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

**File:** contracts/CircomDataBuilder.sol (L97-131)
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

**File:** contracts/CircomDataBuilder.sol (L195-201)
```text
        input[index++] = circomData.rootHashHinkal;
        input[index++] = getSignedMessageHash(
            chainId,
            verifyingContract,
            circomData,
            emporiumMessage
        );
```

**File:** contracts/HinkalHelper.sol (L220-225)
```text

        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
        );
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

**File:** contracts/Hinkal.sol (L58-64)
```text
            require(
                rootHashExists(
                    circomData.rootHashHinkal,
                    circomData.rootHashHinkalIndex
                ),
                "Hinkal Root Hash is Incorrect"
            );
```
