# [H] \[H01\] Votes can be duplicated

## Summary
Severity: High
Source: https://github.com/UMAprotocol/protocol/blob/9d403ddb5f2f07194daefe7da51e0e0a6306f2c4/core/contracts/oracle/implementation/Voting.sol#L315
Type: audit-issue

## Details
The Data Verification Mechanism uses a commit-reveal scheme to hide votes during the voting period. The intention is to prevent voters from simply voting with the majority. However, the current design allows voters to blindly copy each other’s submissions, which undermines this goal.

In particular, each commitment is a [masked hash of the claimed price](https://github.com/UMAprotocol/protocol/blob/9d403ddb5f2f07194daefe7da51e0e0a6306f2c4/core/contracts/oracle/implementation/Voting.sol#L315), but is not cryptographically tied to the voter. This means that anyone can copy the commitment of a target voter (for instance, someone with a large balance) and submit it as their own. When the target voter reveals their salt and price, the copycat can “reveal” the same values. Moreover, if another voter recognizes this has occurred during the commitment phase, they can also change their commitment to the same value, which may become an alternate Schelling point.

Consider including the voter address within the commitment to prevent votes from being duplicated. Additionally, as a matter of good practice, consider including the relevant timestamp, price identifier and round ID as well to limit the applicability (and reusability) of a commitment.

**Update:** _Fixed in [PR#1217](https://github.com/UMAprotocol/protocol/pull/1217). The hash now includes all relevant context to avoid duplication of votes and limit their applicability and reusability._
