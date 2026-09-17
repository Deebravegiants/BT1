# [M] Unclear semantics for Transfer

## Summary
Severity: Medium
Source: https://github.com/ethereum/EIPs/blob/master/EIPS/eip-20-token-standard.md
Type: audit-issue

## Details
The [ERC20 token standard](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-20-token-standard.md) specifies the [Transfer](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-20-token-standard.md#transfer-1) event to log transfers. The specification is informal, and there is not an exact characterization of when the event should be emitted. However, since this event is relied on by applications, it is in the interest of the project to try to respect the semantics that applications expect. This will pay off in a better user experience, and probably lower operational costs.

The `Transfer` event is used throughout `FuelToken` in unexpected and inconsistent ways. When vested tokens are released (via [releaseVanbexTeamTokens](https://github.com/etherparty/FUEL-Contracts/blob/3717b751bb2fa57ae300776a93ee4d7d7beb2c07/contracts/FuelToken.sol#L179)), a [transfer from the token contract itself](https://github.com/etherparty/FUEL-Contracts/blob/3717b751bb2fa57ae300776a93ee4d7d7beb2c07/contracts/FuelToken.sol#L182) is logged. This is conflicting with the expected semantics of the event, because the token contract didn’t have those tokens as part of its balance to begin with. In [transferFromCrowdfund](https://github.com/etherparty/FUEL-Contracts/blob/3717b751bb2fa57ae300776a93ee4d7d7beb2c07/contracts/FuelToken.sol#L169), the event is emitted [with the crowdfund as the source](https://github.com/etherparty/FUEL-Contracts/blob/3717b751bb2fa57ae300776a93ee4d7d7beb2c07/contracts/FuelToken.sol#L174), but there was never a `Transfer` event with the crowdfund as the destination.

Consider emitting this event with the zero address as the `from` field, which is the [accepted way](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-20-token-standard.md#transfer) to log creation of tokens.

_**Update:** Fixed in [759557a](https://github.com/etherparty/FUEL-Contracts/commit/759557a4d5ba55b26f7f55fed514129633d9cca3) and [a363180](https://github.com/etherparty/FUEL-Contracts/commit/a363180b96141e8fdba2affa896c56bc0cbb1c9a)._
