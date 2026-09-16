Confirmed: `HandlerV2.handleConsensus` is a permissionless entry point that fetches `previousState` from `host.consensusState()` (the trusted on-chain state) and forwards it along with an attacker-supplied `proof` to `IConsensusV2(host.consensusClient()).verify(previousState, proof)`, which for the ECDSA path resolves to `EcdsaBeefy.verify` → `verifyMmrUpdateProof` → `verifyMmrLeaf` → `leafIndex`. [1](#0-0) 

Within `EcdsaBeefy.leafIndex`, the subtraction `parentNumber - activationBlock` is unchecked against the relationship between the two: `parentNumber` comes directly from `relay.latestMmrLeaf.parentNumber`, a field fully controlled by the untrusted `proof` bytes supplied by the caller/relayer, while `activationBlock` is `trustedState.beefyActivationBlock`, fixed at consensus-client setup. [2](#0-1) 

### Title
Unvalidated attacker-controlled `parentNumber` causes integer underflow revert (DoS) in `EcdsaBeefy.leafIndex` - (File: evm/src/consensus/EcdsaBeefy.sol)

### Summary
`EcdsaBeefy.leafIndex()` computes `parentNumber - activationBlock` without checking that `parentNumber >= activationBlock`. `parentNumber` is taken verbatim from the relayer-supplied `RelayChainProof.latestMmrLeaf.parentNumber`, an untrusted value in the ABI-encoded `proof` argument that any address can pass to the permissionless `HandlerV2.handleConsensus`. Because the contract compiles under Solidity `^0.8.17`, this underflow triggers a `Panic(0x11)` revert rather than a silent wraparound, but it happens after all `pure`, gas-cheap steps and is reachable before or in place of the cryptographically expensive multi-signature/authority checks fail to catch it (the check on `parentNumber` never validates against `activationBlock` anywhere upstream).

### Finding Description
`verifyMmrUpdateProof` is invoked from `EcdsaBeefy.verify()`, which is the `IConsensusV2` implementation called by `HandlerV2.handleConsensus(IHost host, bytes calldata proof)` — a permissionless function reachable by any relayer/unprivileged transaction submitter. [3](#0-2) 

Inside `verifyMmrUpdateProof`, after passing the supermajority signature check and payload extraction, `verifyMmrLeaf` is called with the untrusted `relay.latestMmrLeaf`: [4](#0-3) 

`verifyMmrLeaf` calls `leafIndex(trustedState.beefyActivationBlock, relay.latestMmrLeaf.parentNumber)`: [5](#0-4) 

`leafIndex` performs the unguarded subtraction: [2](#0-1) 

There is no check anywhere in `verify()`, `verifyMmrUpdateProof()`, or `leafIndex()` that `parentNumber >= activationBlock` before the subtraction is performed. An attacker who forges a `RelayChainProof` (or replays/mutates a previously seen commitment) with a `latestMmrLeaf.parentNumber` smaller than the configured `beefyActivationBlock` — while still satisfying the earlier stale-height check (`consensusState.latestHeight >= relay.signedCommitment.commitment.blockNumber` uses `commitment.blockNumber`, a separate field from `latestMmrLeaf.parentNumber`) and even the supermajority/authority checks (an attacker who has access to any valid supermajority-signed commitment, e.g. captured off-chain or via a previous valid submission, can pair it with a manipulated `latestMmrLeaf.parentNumber`, since the leaf hash is only checked for MMR-proof matching, not cross-validated against `commitment.blockNumber`) — triggers a `Panic(0x11)` underflow revert, aborting `handleConsensus`.

### Impact Explanation
This is a Medium-severity denial-of-service: crafted `latestMmrLeaf.parentNumber` values below `beefyActivationBlock` cause `handleConsensus` to revert deterministically via an arithmetic panic rather than a graceful, catchable domain error. Since `handleConsensus` also underlies `batchCall`, a single malformed consensus-update payload embedded in a batch aborts the entire batch (all other included calls, e.g. `handlePostRequests`, are rolled back too), amplifying the disruption to message delivery for a permissionless relayer network. Repeatedly submitting such proofs can be used to grief relayers or waste their gas, and there is no functional distinction from a legitimate `InvalidMmrProof`-style domain revert — the process fails ungracefully instead of failing with a clear, expected error.

### Likelihood Explanation
Likelihood is high: `latestMmrLeaf.parentNumber` is a leaf field decoded straight from calldata (`abi.decode(proof, (RelayChainProof, ParachainProof))`) with no independent bound-checking against `beefyActivationBlock` prior to the subtraction. No privileged role is required — any account can call `HandlerV2.handleConsensus` with a manipulated proof, and the underflow condition depends solely on picking `parentNumber < beefyActivationBlock`, something entirely at the caller's discretion for the numeric field itself (independent of whether the rest of the MMR/signature proof ultimately validates, the underflow occurs before the MMR-inclusion check `MerkleMountainRange.VerifyProof` is evaluated inside `verifyMmrLeaf`).

### Recommendation
Validate `parentNumber >= activationBlock` in `leafIndex` (or immediately before calling it) and revert with an explicit, descriptive error (e.g. `InvalidParentNumber()`) instead of allowing the raw subtraction to underflow. Alternatively use `parentNumber >= activationBlock ? parentNumber - activationBlock : 0` only if `0` is a semantically valid sentinel, or reject the proof outright since a `parentNumber` below the client's own activation block indicates a malformed/malicious leaf.

### Proof of Concept
1. Deploy `EcdsaBeefy` with a `BeefyConsensusState` where `beefyActivationBlock = N > 0` (a non-zero activation block, a normal configuration for a parachain client whose BEEFY protocol activated after genesis).
2. Craft (or reuse a captured, validly-signed) `RelayChainProof` whose `signedCommitment.commitment.blockNumber > consensusState.latestHeight` (to bypass the stale-proof no-op) and whose `latestMmrLeaf.parentNumber < N`.
3. Submit this proof via `HandlerV2.handleConsensus(host, proof)`.
4. Execution reaches `leafIndex(N, parentNumber)` where `parentNumber < N`, and `parentNumber - activationBlock` underflows `uint256`, causing Solidity's built-in checked-arithmetic to revert with `Panic(0x11)`, aborting the entire transaction (and any batched calls in the same `batchCall`).

### Citations

**File:** evm/src/core/HandlerV2.sol (L144-151)
```text
    function handleConsensus(IHost host, bytes calldata proof) external notFrozen(host) {
        uint256 delay = block.timestamp - host.consensusUpdateTime();
        if (delay >= host.unStakingPeriod()) revert ConsensusClientExpired();

        bytes memory previousState = host.consensusState();
        (bytes memory verifiedState, IntermediateState[] memory intermediates, uint256 nextAuthoritySetId) =
            IConsensusV2(host.consensusClient()).verify(previousState, proof);

```

**File:** evm/src/consensus/EcdsaBeefy.sol (L164-196)
```text
        verifyMmrLeaf(trustedState, relayProof, mmrRoot);
        if (relayProof.latestMmrLeaf.nextAuthoritySet.id > trustedState.nextAuthoritySet.id) {
            trustedState.currentAuthoritySet = trustedState.nextAuthoritySet;
            trustedState.nextAuthoritySet = relayProof.latestMmrLeaf.nextAuthoritySet;
        }
        trustedState.latestHeight = latestHeight;

        return (trustedState, relayProof.latestMmrLeaf.extra);
    }

    // @dev Stack too deep, sigh solidity
    function verifyMmrLeaf(BeefyConsensusState memory trustedState, RelayChainProof memory relay, bytes32 mmrRoot)
        internal
        pure
    {
        bytes32 hash = keccak256(
            Codec.Encode(
                PartialBeefyMmrLeaf({
                    version: relay.latestMmrLeaf.version,
                    parentNumber: relay.latestMmrLeaf.parentNumber,
                    parentHash: relay.latestMmrLeaf.parentHash,
                    nextAuthoritySet: relay.latestMmrLeaf.nextAuthoritySet,
                    extra: relay.latestMmrLeaf.extra
                })
            )
        );
        uint256 leafCount = leafIndex(trustedState.beefyActivationBlock, relay.latestMmrLeaf.parentNumber) + 1;
        MerkleMountainRange.Leaf[] memory leaves = new MerkleMountainRange.Leaf[](1);
        leaves[0] = MerkleMountainRange.Leaf({index: relay.latestMmrLeaf.leafIndex, hash: hash});
        bool valid = MerkleMountainRange.VerifyProof(mmrRoot, relay.mmrProof, leaves, leafCount);

        if (!valid) revert InvalidMmrProof();
    }
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L231-238)
```text
    // @dev Calculates the mmr leaf index for a block whose parent number is given.
    function leafIndex(uint256 activationBlock, uint256 parentNumber) internal pure returns (uint256) {
        if (activationBlock == 0) {
            return parentNumber;
        } else {
            return parentNumber - activationBlock;
        }
    }
```
