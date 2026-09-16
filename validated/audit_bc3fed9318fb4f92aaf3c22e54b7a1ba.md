### Title
Permanent Freezing of Consensus Updates via Stale `_consensusState` Encoding After `consensusClient` Rotation - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost` stores a single opaque `_consensusState` blob that is decoded and re-verified by whichever contract is currently configured as `_hostParams.consensusClient`. `updateHostParams`/`updateHostParamsInternal` allows cross-chain governance (via the `hostManager`) to swap `consensusClient` to any contract that merely satisfies the `IConsensusV2` ERC165 interface — with no check that the new client can decode the state bytes produced by the *previous* client. This is structurally the same bug class as the referenced Paladin finding: an admin-settable dependency (`lootCreator` / `consensusClient`) is rotated while other on-chain state that is *coupled to the old dependency's data format* (`totalQuestPeriodRewards` / `_consensusState`) is left untouched, so the next ordinary, unprivileged call into the new dependency (`_createLoot` claim / `handleConsensus` proof submission) reverts irrecoverably.

### Finding Description
`_consensusState` is declared once, globally, per host: [1](#0-0) 

`consensusClient` is a single mutable address in `HostParams`, swappable by governance through `updateHostParams`: [2](#0-1) 

`updateHostParamsInternal` only checks that the new `consensusClient` has code and implements the `IConsensusV2` interface — it never checks that the new client can decode the `_consensusState` bytes already committed under the *previous* client's encoding: [3](#0-2) [4](#0-3) 

The only path that advances `_consensusState` going forward is `HandlerV2.handleConsensus`, callable by any relayer, which reads the *existing* (stale-format) state and feeds it straight into the *newly configured* client's `verify`: [5](#0-4) 

Different consensus-client implementations in this codebase (e.g. `EcdsaBeefy` vs `SP1Beefy`, and by extension any GRANDPA/BSC/Tendermint/sync-committee client that could occupy the same `consensusClient` slot) use their own `ConsensusState`/proof struct layouts: [6](#0-5) 

Because `_consensusState` is never reset or migrated on rotation, and because `updateHostParamsInternal` performs no compatibility check between the old and new encodings, a legitimate governance action to rotate `consensusClient` (documented as a supported operational flow — see the deployment script that reads current `hostParams()` and overwrites only `consensusClient`) can leave the host holding bytes the new client cannot parse: [7](#0-6) 

From that point on, every call to `handleConsensus` — the sole, permissionless, single-transaction entry point by which any relayer advances consensus and thereby state-machine commitments — decodes `previousState` inside the new client's `verify()` and either reverts or (in the worst case) silently misinterprets it. Since `storeConsensusState`/`storeStateMachineCommitment` are only reachable through this same path, consensus updates for the affected destination stop advancing entirely.

### Impact Explanation
This is a route-freezing bug: once `_consensusState` becomes format-incompatible with the active `consensusClient`, the destination host can never again accept a new consensus proof, which cascades into an inability to accept any new state-machine commitments, which in turn blocks every downstream cross-chain message (POST/GET requests, responses, timeouts) that must be proven against that host — a permanent freeze of message delivery for the whole chain, matching the "route unable to deliver messages" impact bucket. Unlike a malicious-admin scenario, this can occur from a well-intentioned, documented consensus-client rotation (upgrading BEEFY verifier implementations, migrating verification schemes, emergency-patching a buggy client) exactly as the original report describes an unintended side effect of an otherwise legitimate `setLootCreator` call.

### Likelihood Explanation
Medium. Consensus-client rotation via `updateHostParams` is an explicitly supported and exercised operational flow (see the deployment script swapping `consensusClient` while reusing existing `hostParams()`), and nothing in `updateHostParamsInternal` validates that `_consensusState`'s encoding survives the swap. The trigger condition (an incompatible encoding between old and new client) depends on which client implementations are involved, but the protocol explicitly supports heterogeneous consensus algorithms behind the same `consensusClient` slot (BEEFY, SP1, and other client types referenced across the codebase), making an eventual incompatible rotation plausible during normal protocol evolution rather than requiring an adversarial actor.

### Recommendation
On any `consensusClient` change in `updateHostParamsInternal`, either (a) require the new client to explicitly re-initialize/re-encode `_consensusState` (e.g., via a dedicated migration call proven to succeed before the swap commits), or (b) require that the new client's `verify` be tolerant of/able to translate the previous encoding, with an on-chain sanity check (e.g., a dry-run decode) performed as part of the governance update itself so an incompatible rotation reverts atomically instead of bricking the host after the fact.

### Proof of Concept
1. Host is live with `consensusClient = ClientA`, and `_consensusState` holds bytes encoded per `ClientA`'s `ConsensusState` struct.
2. Governance dispatches `SetHostParam`/`updateHostParams` through the `hostManager`, setting `consensusClient = ClientB`, where `ClientB.verify` expects a structurally different `ConsensusState` encoding. `updateHostParamsInternal` only checks `ClientB` supports `IConsensusV2` via ERC165 and applies the change — no state-compatibility check is performed (`evm/src/core/EvmHost.sol:599-636`).
3. Any relayer subsequently calls `HandlerV2.handleConsensus(host, proof)`. It reads `previousState = host.consensusState()` (still `ClientA`-encoded) and calls `IConsensusV2(ClientB).verify(previousState, proof)` (`evm/src/core/HandlerV2.sol:148-150`).
4. `ClientB.verify` fails to decode `previousState` and reverts (or returns an incorrect state if decoding happens to succeed on malformed input).
5. Every subsequent relayer submission hits the same failure; `_consensusState` can never be advanced again, and no new state-machine commitments can be stored for that host, freezing all message delivery routed through it.

### Citations

**File:** evm/src/core/EvmHost.sol (L152-157)
```text

    // Current verified state of the consensus client;
    bytes private _consensusState;

    // Timestamp for when the consensus was most recently updated
    uint256 private _consensusUpdateTimestamp;
```

**File:** evm/src/core/EvmHost.sol (L573-576)
```text
    function updateHostParams(HostParams memory params) external virtual restrict(_hostParams.hostManager) {
        updateHostParamsInternal(params);
    }

```

**File:** evm/src/core/EvmHost.sol (L599-605)
```text
        if (
            params.consensusClient == address(0) || address(params.consensusClient).code.length == 0
                || !IERC165(params.consensusClient).supportsInterface(type(IConsensusV2).interfaceId)
        ) {
            // otherwise cannot process new consensus datagrams
            revert InvalidConsensusClient();
        }
```

**File:** evm/src/core/EvmHost.sol (L623-636)
```text
        // safe to emit here because invariants have already been checked
        // and don't want to store a temp variable for the old params
        emit HostParamsUpdated({oldParams: _hostParams, newParams: params});

        _hostParams.feeToken = params.feeToken;
        _hostParams.admin = params.admin;
        _hostParams.handler = params.handler;
        _hostParams.hostManager = params.hostManager;
        _hostParams.uniswapV2 = params.uniswapV2;
        _hostParams.unStakingPeriod = params.unStakingPeriod;
        _hostParams.challengePeriod = params.challengePeriod;
        _hostParams.consensusClient = params.consensusClient;
        _hostParams.stateMachines = params.stateMachines;
        _hostParams.hyperbridge = params.hyperbridge;
```

**File:** evm/src/core/HandlerV2.sol (L144-153)
```text
    function handleConsensus(IHost host, bytes calldata proof) external notFrozen(host) {
        uint256 delay = block.timestamp - host.consensusUpdateTime();
        if (delay >= host.unStakingPeriod()) revert ConsensusClientExpired();

        bytes memory previousState = host.consensusState();
        (bytes memory verifiedState, IntermediateState[] memory intermediates, uint256 nextAuthoritySetId) =
            IConsensusV2(host.consensusClient()).verify(previousState, proof);

        if (keccak256(previousState) == keccak256(verifiedState)) return;
        host.storeConsensusState(verifiedState);
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L151-172)
```text
        // verify the commitment
        bytes32 commitmentHash = keccak256(Codec.Encode(commitment));
        MerkleMultiProof.Leaf[] memory authorities = new MerkleMultiProof.Leaf[](sigLen);
        for (uint256 i = 0; i < sigLen; i++) {
            Vote memory vote = relayProof.signedCommitment.votes[i];
            address authority = ECDSA.recover(commitmentHash, vote.signature);
            authorities[i] =
                MerkleMultiProof.Leaf({index: vote.authorityIndex, hash: keccak256(abi.encodePacked(authority))});
        }

        bool valid = MerkleMultiProof.VerifyProof(authoritySet.root, relayProof.proof, authorities, authoritySet.len);
        if (!valid) revert InvalidAuthoritiesProof();

        verifyMmrLeaf(trustedState, relayProof, mmrRoot);
        if (relayProof.latestMmrLeaf.nextAuthoritySet.id > trustedState.nextAuthoritySet.id) {
            trustedState.currentAuthoritySet = trustedState.nextAuthoritySet;
            trustedState.nextAuthoritySet = relayProof.latestMmrLeaf.nextAuthoritySet;
        }
        trustedState.latestHeight = latestHeight;

        return (trustedState, relayProof.latestMmrLeaf.extra);
    }
```

**File:** evm/script/DeployHostUpdates.s.sol (L40-48)
```text
        // Update host params if not mainnet
        bool isMainnet = config.get("is_mainnet").toBool();
        if (!isMainnet) {
            HostParams memory params = EvmHost(HOST_ADDRESS).hostParams();
            params.consensusClient = address(consensusClient);
            // params.handler = address(handler);
            EvmHost(HOST_ADDRESS).updateHostParams(params);
            console.log("Host params updated with new consensus client and handler");
        }
```
