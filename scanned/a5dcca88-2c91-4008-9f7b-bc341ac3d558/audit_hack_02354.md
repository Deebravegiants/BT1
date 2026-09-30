# [M] \[M01\] Fees cannot be collected

## Summary
Severity: Medium
Source: https://github.com/primitivefinance/primitive-protocol/blob/78a8e64b7618e9199203ab84042876c580ae1e90/packages/primitive-contracts/contracts/option/primitives/Option.sol#L179
Type: audit-issue

## Details
The [exercise function](https://github.com/primitivefinance/primitive-protocol/blob/78a8e64b7618e9199203ab84042876c580ae1e90/packages/primitive-contracts/contracts/option/primitives/Option.sol#L179) of the `Option` contract charges a fee every time a user exercises option tokens or takes a flash loan of underlying tokens. This fee is calculated [as a portion of the underlying tokens](https://github.com/primitivefinance/primitive-protocol/blob/78a8e64b7618e9199203ab84042876c580ae1e90/packages/primitive-contracts/contracts/option/primitives/Option.sol#L225) sent out by the contract, and is expected to [be paid by the caller in strike tokens](https://github.com/primitivefinance/primitive-protocol/blob/78a8e64b7618e9199203ab84042876c580ae1e90/packages/primitive-contracts/contracts/option/primitives/Option.sol#L216).

Before finishing execution of the `exercise` function, the cached balances of strike and underlying tokens [are updated](https://github.com/primitivefinance/primitive-protocol/blob/78a8e64b7618e9199203ab84042876c580ae1e90/packages/primitive-contracts/contracts/option/primitives/Option.sol#L250) to the latest balance [queried during the transaction](https://github.com/primitivefinance/primitive-protocol/blob/78a8e64b7618e9199203ab84042876c580ae1e90/packages/primitive-contracts/contracts/option/primitives/Option.sol#L208-L213). However, the logic does not keep track of the added fees. Thus they will be lost without any possibility of collecting them.

Consider modifying the way in which fees are tracked so that they can be effectively collected. Related issue **“\[H01\] Fragile internal accounting mechanism may cause loss of funds”** should be taken into account to solve this particular issue. Alternatively, if fees do not have a clear purpose in the Primitive protocol, consider removing them from the system altogether.

**Update:** _Fixed in [PR #16](https://github.com/primitivefinance/primitive-protocol/pull/16). The concept of fee has been removed from the system altogether. The docstrings [above the exercise function](https://github.com/primitivefinance/primitive-protocol/blob/hotfix/audit-fixes/packages/primitive-contracts/contracts/option/primitives/Option.sol#L173) must be updated to reflect this._
