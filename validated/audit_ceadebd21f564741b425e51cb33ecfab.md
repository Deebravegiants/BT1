This confirms `BandwidthManager.setHost` is a one-shot, owner-triggered configuration step analogous to the reported bug class. If the owner passes the wrong `hostAddr` (or any address that is not the real ISMP host they intend to use, e.g. a placeholder, wrong-chain host, or unreachable/EOA address), `_host` becomes permanently locked to that value since `setHost` reverts with `UnauthorizedAction` once `_host != address(0)`.### Title
Operator error in one-shot `EvmHost.setConsensusState` can permanently brick a route's message delivery - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.setConsensusState` is a one-shot admin function, gated by `_canReinitConsensus()`, that seeds the initial consensus state, height, and state commitment for a route. Once `_consensusState` is non-empty, the admin can never call it again; from that point forward the state can only be advanced by `HandlerV2` via consensus proofs that are themselves verified *against* the currently stored state. If the admin seeds the wrong initial state (wrong authority set, wrong height/commitment, malformed encoding for the chain's consensus client), every subsequent proof submitted through `HandlerV2.handleConsensusMessage`/`verify` will fail to validate against that broken baseline, and there is no recovery path on mainnet hosts — permanently freezing the route's ability to deliver any message (and, transitively, any funds gated behind state/membership proofs on that route).

### Finding Description
`setConsensusState` is restricted to the admin and is intentionally one-shot: [1](#0-0) 

```solidity
function _canReinitConsensus() internal view virtual returns (bool) {
    return keccak256(_consensusState) == keccak256(bytes(""));
}

function setConsensusState(bytes memory state, StateMachineHeight memory height, StateCommitment memory commitment)
    public
    restrict(_hostParams.admin)
{
    if (!_canReinitConsensus()) revert UnauthorizedAction();
    _consensusState = state;
    _consensusUpdateTimestamp = block.timestamp;
    _stateCommitments[height.stateMachineId][height.height] = commitment;
    _stateCommitmentsUpdateTime[height.stateMachineId][height.height] = block.timestamp;
    _latestStateMachineHeight[height.stateMachineId] = height.height;
}
```

Once `_consensusState` is non-empty, `_canReinitConsensus()` returns `false` forever on the default (mainnet) `EvmHost`, so the admin has exactly one chance to get `state`, `height`, and `commitment` right. Only `TestnetHost` overrides `_canReinitConsensus()` to permit repeated re-initialization — production hosts do not have that escape hatch.

From then on, the only path that can update the consensus state is `HandlerV2`, which decodes proofs and verifies them against the *currently trusted* `previousState`: [2](#0-1) 

```solidity
if (keccak256(previousState) == keccak256(verifiedState)) return;
host.storeConsensusState(verifiedState);

uint256 intermediatesLen = intermediates.length;
for (uint256 i = 0; i < intermediatesLen; i++) {
    ...
    host.storeStateMachineCommitment(stateMachineHeight, intermediate.commitment);
}
```

If the seeded `_consensusState` (or its paired height/commitment) is wrong — e.g., an operator mistakenly encodes the wrong authority set, wrong `BeefyConsensusState`/light-client parameters, or a stale height — every subsequent consensus proof that is checked against it in `IConsensusV2.verify` (see the BEEFY implementation, which strictly compares heights and authority-set ids against the stored state) will either be rejected as stale/invalid or will validate to a state the real chain never produced. There is no admin override to fix this once set, unlike the `MerklePayoutStrategyImplementation.updateDistribution` bug where the flag (`isReadyForPayout`) is separately, irrevocably locked by another contract while the payload it depends on (`merkleRoot`) can be silently left at a wrong/default value with no way back.

### Impact Explanation
A route whose consensus state is bricked this way can never again produce accepted `handleConsensusMessage`, `handlePostRequests`, `handleGetResponses`, or membership/non-membership proofs for that source chain, because `HandlerV2` and downstream apps depend on `host.stateMachineCommitment(...)` / `latestStateMachineHeight(...)` being correctly and monotonically advanced from a valid baseline. This directly matches the accepted impact category "a route unable to deliver messages": relayer fee accumulation/withdrawal proofs, token-bridge mint/burn settlement, and intents fill/cancel/refund proofs that rely on state or GET-response proofs from that chain all become permanently undeliverable, freezing in-flight funds (escrowed intents, relayer-accrued fees, bridge-locked collateral) on that route with no operator-side recovery — the contract would need to be redeployed and re-registered network-wide.

### Likelihood Explanation
This requires the chain admin to make an error while performing the single, non-repeatable `initialize`/`setConsensusState` bring-up step for a new EVM host deployment — exactly the "operator error" scenario the original report flags, not an attacker action. Given the state parameters are chain/consensus-client-specific ABI-encoded structs (e.g. `BeefyConsensusState`, authority set ids, MMR roots) assembled off-chain and passed once, a mismatch between the deployment tooling and the actual live consensus state at genesis is a realistic operational risk, especially across many chains where `EvmHost` is deployed per the CREATE2 parity requirements described in the constructor's own comments.

### Recommendation
Provide a bounded, governance-gated recovery path for a misconfigured initial consensus state rather than making `setConsensusState` unconditionally one-shot on mainnet hosts — for example, allow the admin (or a slower governance-only path) to re-seed consensus state only when `_latestStateMachineHeight` for every registered state machine is still at its initial/unchanged value (i.e., no real progress has been recorded yet), so a same-block or same-epoch correction is possible without weakening the trust model once genuine chain progress has been accepted.

### Proof of Concept
1. Deploy `EvmHost` and call `initialize(params)` (admin-only, one-shot) to set `_hostParams`.
2. Admin calls `setConsensusState(state, height, commitment)` with an incorrectly encoded `state` (or wrong `height`/`commitment` pairing) for the paired `IConsensusV2` client (e.g., `EcdsaBeefy`/`SP1`), as in [3](#0-2) .
3. `_consensusState` is now non-empty; `_canReinitConsensus()` permanently returns `false`, so any second `setConsensusState` call reverts with `UnauthorizedAction`.
4. Every later `HandlerV2.handleConsensusMessage` call decodes the wrong `previousState` and either fails `IConsensusV2.verify`'s internal checks (e.g. `UnknownAuthoritySet`/`InvalidAuthoritiesProof` in `EcdsaBeefy.verifyMmrUpdateProof`, [4](#0-3) ) or advances to a state the real chain cannot match, so no further legitimate consensus update, and therefore no state/membership proof for that route, can ever be accepted again.
5. Any funds already escrowed/awaiting settlement through that route (intents, relayer fees, bridged tokens) become permanently unrecoverable through normal protocol flows.

### Citations

**File:** evm/src/core/EvmHost.sol (L762-788)
```text
    function _canReinitConsensus() internal view virtual returns (bool) {
        return keccak256(_consensusState) == keccak256(bytes(""));
    }

    /**
     * @dev sets the initial consensus state. By default this is a one-shot
     * operation: once `_consensusState` is non-empty the admin can no longer
     * call this and consensus state moves only through `storeConsensusState`
     * (handler-only, driven by consensus proofs). `TestnetHost` overrides
     * `_canReinitConsensus` to lift this restriction.
     * @param state initial consensus state
     * @param height initial state-machine height
     * @param commitment initial state commitment at `height`
     */
    function setConsensusState(bytes memory state, StateMachineHeight memory height, StateCommitment memory commitment)
        public
        restrict(_hostParams.admin)
    {
        if (!_canReinitConsensus()) revert UnauthorizedAction();

        _consensusState = state;
        _consensusUpdateTimestamp = block.timestamp;

        _stateCommitments[height.stateMachineId][height.height] = commitment;
        _stateCommitmentsUpdateTime[height.stateMachineId][height.height] = block.timestamp;
        _latestStateMachineHeight[height.stateMachineId] = height.height;
    }
```

**File:** evm/src/core/HandlerV2.sol (L151-164)
```text

        if (keccak256(previousState) == keccak256(verifiedState)) return;
        host.storeConsensusState(verifiedState);

        uint256 intermediatesLen = intermediates.length;
        for (uint256 i = 0; i < intermediatesLen; i++) {
            IntermediateState memory intermediate = intermediates[i];
            uint256 latestHeight = host.latestStateMachineHeight(intermediate.stateMachineId);
            if (latestHeight != 0 && intermediate.height > latestHeight) {
                StateMachineHeight memory stateMachineHeight =
                    StateMachineHeight({stateMachineId: intermediate.stateMachineId, height: intermediate.height});
                host.storeStateMachineCommitment(stateMachineHeight, intermediate.commitment);
            }
        }
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L130-149)
```text
        if (
            commitment.validatorSetId != trustedState.currentAuthoritySet.id
                && commitment.validatorSetId != trustedState.nextAuthoritySet.id
        ) {
            revert UnknownAuthoritySet();
        }

        bool isCurrentAuthorities = commitment.validatorSetId == trustedState.currentAuthoritySet.id;
        AuthoritySetCommitment memory authoritySet =
            isCurrentAuthorities ? trustedState.currentAuthoritySet : trustedState.nextAuthoritySet;
        if (!checkParticipationThreshold(sigLen, authoritySet.len)) revert SuperMajorityRequired();

        uint256 payloadLength = commitment.payload.length;
        bytes32 mmrRoot;
        for (uint256 i = 0; i < payloadLength; i++) {
            if (commitment.payload[i].id == MMR_ROOT_PAYLOAD_ID && commitment.payload[i].data.length == 32) {
                mmrRoot = Bytes.toBytes32(commitment.payload[i].data);
            }
        }
        if (mmrRoot == bytes32(0)) revert MmrRootHashMissing();
```
