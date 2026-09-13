# [H] Invalid DISPUTED_L2_BLOCK_NUMBER is passed to VM

## Summary
Severity: High
Chain: Smart contract
Component: 2024-07-optimism
Published: 2024-07-29
Source: https://github.com/code-423n4/2024-07-optimism-findings/issues/36
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-07-optimism/blob/70556044e5e080930f686c4e5acde420104bb2c4/packages/contracts-bedrock/src/dispute/FaultDisputeGame.sol#L453


# Vulnerability details

## Impact
The span of the game tree at split depth is far larger than the length between the starting block and the claimed block, when `starting block + trace index + 1 > claimed block`, honest party should continue to commit to the root of the claimed block. However, the DISPUTED_L2_BLOCK_NUMBER passed to the VM is always `starting block + trace index + 1`, which means the op-program (at inter-block perspective) will not stop until it reached the l2 safe head(corresponding to parenthash), and if the claimed block is earlier than the safe head, it can be challenged and will be considered invalid.

## Proof of Concept
Since op-program is out of scope of this contest, this report will not spend too much time in proving *block earlier than safe head can be challenged*, instead it will only show the inconsistency within the smart contract part.

For simplicity, we assume the span of the game tree at split depth is 8 and starting block is 0. At block level, we use **defend a ->p b** to refer to commit a valid VM trace with a as starting output, b as disputed output, p as disputed block number and VALID as the final state, similarly **attack a ->p b** refers to commit a valid VM trace with ... and INVALID or PANIC as the final state. We use Bi to refer to the valid L2 root at block i.

Suppose Alice made a valid root claim B2 for block 2, Bob made a valid root claim B3 for block 3 and they claim at the same L1 block (so the stored l1Head will be the identical). Ideally, both of them should be able to defend their claim. We already know that Bob can **defend B2 ->3 B3** in his own game. What if Bob tries to attack Alice in her game? 

(Recall Alice's view of valid state is 12222222 and Bob's is 12333333)
1. Bob attacks by claiming B3. (trace index 3)
2. Alice attacks by claiming B2. (trace index 1)
3. Bob defends by claiming B3. (trace index 2)
4. Alice **attacks B2 ->3 B3**. (disputed block = starting block + trace index + 1 = 3)
```
    /// @inheritdoc IFaultDisputeGame
    function addLocalData(uint256 _ident, uint256 _execLeafIdx, uint256 _partOffset) external {
        // INVARIANT: Local data can only be added if the game is currently in progress.
        if (status != GameStatus.IN_PROGRESS) revert GameNotInProgress();

        (Claim starting, Position startingPos, Claim disputed, Position disputedPos) =
            _findStartingAndDisputedOutputs(_execLeafIdx);
        Hash uuid = _computeLocalContext(starting, startingPos, disputed, disputedPos);

        IPreimageOracle oracle = VM.oracle();
        if (_ident == LocalPreimageKey.L1_HEAD_HASH) {
            // Load the L1 head hash
            oracle.loadLocalData(_ident, uuid.raw(), l1Head().raw(), 32, _partOffset);
        } else if (_ident == LocalPreimageKey.STARTING_OUTPUT_ROOT) {
            // Load the starting proposal's output root.
            oracle.loadLocalData(_ident, uuid.raw(), starting.raw(), 32, _partOffset);
        } else if (_ident == LocalPreimageKey.DISPUTED_OUTPUT_ROOT) {
            // Load the disputed proposal's output root
            oracle.loadLocalData(_ident, uuid.raw(), disputed.raw(), 32, _partOffset);
        } else if (_ident == LocalPreimageKey.DISPUTED_L2_BLOCK_NUMBER) {
            // Load the disputed proposal's L2 block number as a big-endian uint64 in the
            // high order 8 bytes of the word.

            // We add the index at depth + 1 to the starting block number to get the disputed L2
            // block number.
            uint256 l2Number = startingOutputRoot.l2BlockNumber + disputedPos.traceIndex(SPLIT_DEPTH) + 1;

            oracle.loadLocalData(_ident, uuid.raw(), bytes32(l2Number << 0xC0), 8, _partOffset);
        } else if (_ident == LocalPreimageKey.CHAIN_ID) {
            // Load the chain ID as a big-endian uint64 in the high order 8 bytes of the word.
            oracle.loadLocalData(_ident, uuid.raw(), bytes32(L2_CHAIN_ID << 0xC0), 8, _partOffset);
        } else {
            revert InvalidLocalIdent();
        }
    }
```
However, all VM inputs above are identical for B2 ->3 B3 in these two cases. Since VM step is deterministic, **B2 ->3 B3** cannot be defended in one game while attacked in another, which shows the contradiction. The problem is that claimed block number is not passed to the VM, so the VM cannot differentiate the context between the two games.


## Recommended Mitigation Steps
    uint256 l2Number = min(startingOutputRoot.l2BlockNumber + disputedPos.traceIndex(SPLIT_DEPTH) + 1, l2BlockNumber());

## Note
```
func (d *Driver) ValidateClaim(l2ClaimBlockNum uint64, claimedOutputRoot eth.Bytes32) error {
	l2Head := d.SafeHead()
	outputRoot, err := d.l2OutputRoot(min(l2ClaimBlockNum, l2Head.Number))
	if err != nil {
		return fmt.Errorf("calculate L2 output root: %w", err)
	}
	d.logger.Info("Validating claim", "head", l2Head, "output", outputRoot, "claim", claimedOutputRoot)
	if claimedOutputRoot != outputRoot {
		return fmt.Errorf("%w: claim: %v actual: %v", ErrClaimNotValid, claimedOutputRoot, outputRoot)
	}
	return nil
}
```
Here l2ClaimBlockNum is just DISPUTED_L2_BLOCK_NUMBER, so DISPUTED_L2_BLOCK_NUMBER clearly should be capped at claimed l2 block number, otherwise the inter-block op-program execution will never stop until it reaches safe head, which means all claims earlier than safe head is invalid in op-program's perspective.


## Assessed type

Context
