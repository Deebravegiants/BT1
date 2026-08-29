# [?] feat: protect epoch-proof fees against an unsound verifier

## Summary
Severity: Unknown
Chain: Aztec
Component: AztecProtocol/aztec-packages
Published: 2026-06-19
Source: https://github.com/AztecProtocol/aztec-packages/commit/8b1ea21eda573bcdb1bc5562ef36b164e8dd8a6e
Type: security-commit

## Details
feat: protect epoch-proof fees against an unsound verifier

Port of #24186 to the v5 release line.

Bind per-checkpoint fee recipient/value to the committee-attested checkpoint
header instead of prover-supplied calldata, so reward distribution and the epoch
proof's fee-region public inputs are derived from headers verified on L1 and no
longer depend on a sound verifier.

- L1: add ProposedHeader.accumulatedFees (hashed in ProposedHeaderLib); replace
  SubmitEpochRootProofArgs.fees[] with headers[]; submitEpochRootProof rehashes
  each supplied header against the stored hash; RewardLib and
  getEpochProofPublicInputs read recipient/value from the verified headers.
- Circuits: add accumulated_fees to CheckpointHeader (hash + serialize) and set
  it in the checkpoint-root composer; bump CHECKPOINT_HEADER_LENGTH.
- Off-chain: thread checkpoint headers from the prover node's epoch session
  through the proof-publishing service to the L1 submit call; archiver, sequencer
  and stdlib carry the new field.
- PXE: bump PXE_DATA_SCHEMA_VERSION (8 -> 9) for the checkpoint serialization
  change and regenerate the storage compatibility snapshots.
