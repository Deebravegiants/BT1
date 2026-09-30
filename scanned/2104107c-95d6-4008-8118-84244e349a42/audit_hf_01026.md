# [M] Unvalidated ProposerIndex in BeaconBlock

## Summary
Severity: Medium
Contest weight: 0.4496
Dataset id: 3812
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During the ProcessProposal() period in cometBFT, validators currently do not explicitly check to ensure that the ProposerIndex in the proposed BeaconBlock is the correct index for the proposer chosen by cometBFT. Down the line, the ProposerIndex is almost fully verified implicitly during the RANDAO reveal signature check at state-transition/pkg/core/state_processor_randao.go#L73, due to the correlation of grabbing the validators public key via the ProposerIndex:
```solidity
proposer, err := st.ValidatorByIndex(blk.GetProposerIndex())
// ...
signingRoot := fd.ComputeRandaoSigningRoot(
    sp.cs.DomainTypeRandao(), epoch,
)
reveal := body.GetRandaoReveal()
if err = sp.signer.VerifySignature(
    proposer.GetPubkey(),
    signingRoot[:],
    reveal,
)
```
However, this remains vulnerable. Here is an example scenario in which this check can be bypassed:
• ProposerA proposes and distributes a block, but due to network errors, less than the quorum amount of validators receive the block.
• cometBFT will move on and ask the next proposer for a block. It chooses ProposerB.
• ProposerB is a malicious validator and had received the previously proposed block from ProposerA that didn't end up getting quorum.
• ProposerB now sets its ProposerIndex to the index of ProposerA and also uses the same RandaoReveal that it saw in ProposerA's proposed block. Since the proposed BeaconBlock is at the same slot, the fd.ComputeRandaoSigningRoot() is the same and the copied RandaoReveal is valid.
• ProposerB now proposes its new block, pretending to be ProposerA from the BeaconBlock perspective. This could result in the penalization of ProposerA if there's any slashing conditions, as well as bypassing the IsSlashed() check at state-transition/pkg/core/state_processor.go#L421.

## Recommendation
Explicitly correlate and validate the ProposerIndex with the proposer's public key from the cometBFT ProcessProposalRequest.
