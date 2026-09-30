# [H] ValidateVoteExtensions function in Cosmos SDK may allow incorrect voting power assumptions in github.com/cosmos/cosmos-sdk

## Summary
Severity: High
Advisory: GO-2024-2638
Aliases: GHSA-95rx-m9m5-m94v
Package: github.com/cosmos/cosmos-sdk
Published: 2024-05-10
Source: https://osv.dev/vulnerability/GO-2024-2638
Type: chain-advisory

## Affected
- Go: `github.com/cosmos/cosmos-sdk` — affected >=0.50.0 <0.50.5

## Details
The default ValidateVoteExtensions helper function infers total voting power based on the injected VoteExtension, which are injected by the proposer.

If your chain utilizes the ValidateVoteExtensions helper in ProcessProposal, a dishonest proposer can potentially mutate voting power of each validator it includes in the injected VoteExtension, which could have potentially unexpected or negative consequences on modified state. Additional validation on injected VoteExtension data was added to confirm voting power against the state machine.

## References
- https://github.com/cosmos/cosmos-sdk/security/advisories/GHSA-95rx-m9m5-m94v
- https://github.com/cosmos/cosmos-sdk/commit/4467110df40797ebe916c23ebfd45c9ee7583897
- https://github.com/cosmos/cosmos-sdk/releases/tag/v0.50.5
