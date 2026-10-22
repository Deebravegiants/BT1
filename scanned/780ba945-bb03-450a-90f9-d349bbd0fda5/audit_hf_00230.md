# [M] arbitraryCall

## Summary
Severity: Medium
Contest weight: 0.2141
Dataset id: 1187
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`arbitraryCall()`'s (L733) use case is to claim airdrops by “gov”. If the address “who” is a token that could be send as an incentive by an attacker via `createIncentive()` then such claim can be made unusable, because on L735 there is a `require(incentives[who] == 0, "inc");` that reverts if a “who” token was received as an incentive.

In this case the `incentives[who]` can be set to 0 by the stream creator by calling `claimIncentive()` but only after the stream has ended according to `require(block.timestamp >= endStream, "stream");` (L520)

If the airdrop is only claimable before the end of the stream, then the airdrop can never be claimed.

If “gov” is not the stream creator then the stream creator must become also the “gov” because `claimIncentive()` only can be called by the stream creator and the `arbitraryCall()` only by “gov”. If resetting `incentives[who]` to 0 by calling `claimIncentive()` and `arbitraryCall()` for the “who” address doesn’t happen atomic, an attacker can send between those two calls again a “who” token.

## Proof of Concept
* <https://github.com/code-423n4/2021-11-streaming/blob/56d81204a00fc949d29ddd277169690318b36821/Streaming/src/Locke.sol#L733>
  * <https://github.com/code-423n4/2021-11-streaming/blob/56d81204a00fc949d29ddd277169690318b36821/Streaming/src/Locke.sol#L500>

## Recommendation
* Best option at the moment I can think of is to accept the risk but clearly communicate to users that this can happen

> Yep this is the tradeoff being made. To maintain trustlessness, we cannot remove the `incentives[who] == 0` check. Additionally, governance shouldn’t be in charge of an arbitrary stream’s `recoverTokens` function. 
> 
> The upshot of this is most `MerkleDrop` contracts are generally external of the token itself and not baked into the ERC20 itself. If a user wants to grief governance, they could continuously `createIncentive` after the stream creator claims the previous. But it does cost the user.
