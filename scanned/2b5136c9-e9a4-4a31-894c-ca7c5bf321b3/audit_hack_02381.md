# [M] \[M02\] Bypassing token events

## Summary
Severity: Medium
Source: https://github.com/pooltogether/pooltogether-contracts/tree/78ac6863f4616269f7d04a0ddd1d60bdfc454937/contracts/ERC777Pool.sol#L442-L443
Type: audit-issue

## Details
Pool Tokens can be redeemed by calling the `burn` function on the `ERC777Pool` contract. This will [emit the Burned and Transfer events](https://github.com/pooltogether/pooltogether-contracts/tree/78ac6863f4616269f7d04a0ddd1d60bdfc454937/contracts/ERC777Pool.sol#L442-L443).

However, users can also call the [withdraw function](https://github.com/pooltogether/pooltogether-contracts/tree/78ac6863f4616269f7d04a0ddd1d60bdfc454937/contracts/BasePool.sol#L493), which does not emit the events, to redeem their full balance of underlying tokens.

This will prevent users from reacting to these state changes from the ERC777 events (although if they are aware of the code structure they could respond to the `Withdrawn` event). It also means that the `Minted` and `Burned` events will not track the total token supply. Note that the `Withdrawn` event does not compensate for this because it does not distinguish between committed balances, open draw balances, sponsorship balances, and fees. Consider either preventing the `withdraw` function from applying to committed deposits (that have corresponding Pool tokens), or otherwise modifying it to emit the appropriate events.

Note: this issue is related to [**“\[L05\] Conflated balances”**](#l05) and any mitigation should consider them both simultaneously.

**Update**: _Fixed in [PR#4](https://github.com/pooltogether/pooltogether-contracts/pull/4/commits/85fb9a8f05824b8aabde22795f2eb0408e8401da). The `Minted` and `Burned` events are emitted when committed balances are withdrawn from the pool._
