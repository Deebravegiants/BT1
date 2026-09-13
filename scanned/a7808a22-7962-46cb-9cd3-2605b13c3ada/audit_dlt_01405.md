# [?] Merge bitcoin/bitcoin#34908: rpc, refactor: gettxoutsetinfo race condition fix follow-ups

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2026-04-20
Source: https://github.com/bitcoin/bitcoin/commit/b6d1b65062ab123248e4f209fe3f63118f03bad6
Type: security-commit

## Details
Merge bitcoin/bitcoin#34908: rpc, refactor: gettxoutsetinfo race condition fix follow-ups

3e5dc610353ef16b0e7f391faaac77da6f4a0fab rpc, refactor: gettxoutsetinfo race condition fix follow-ups (rkrux)

Pull request description:

  This patch addresses my own review comments from the review of #34451. If these are found helpful, it makes sense to do them now after the previous PR was merged and backported.

  Pasting the comments below that also explains the changes:

  - Move the pindex declaration below now that it is not used earlier.
  - stats was being generated partially in both these ComputeUTXOStats functions, which reads oddly to me. Now that the pcursor is also moved and passed to this function, which reads oddly as well, I believe we can refactor this function to completely build the stats inside this function. A side benefit is that by removing the stats and pcursor arguments, the function signature becomes quite similar to its namesake, which in turn becomes a straightforward wrapper of this function.

ACKs for top commit:
  w0xlt:
    ACK 3e5dc610353ef16b0e7f391faaac77da6f4a0fab
  sedited:
    ACK 3e5dc610353ef16b0e7f391faaac77da6f4a0fab

Tree-SHA512: b8e4a4ebfe4935aa97920cb7068445ea93e571f80e679b8791343ac8750b48484d4288e083e07bf433b397cb6071171a2b77d34758a4627056b34cc63d06f0f4
