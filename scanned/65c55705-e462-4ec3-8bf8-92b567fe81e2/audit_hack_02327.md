# [M] \[M08\] Excessive indirection

## Summary
Severity: Medium
Source: https://github.com/holdefi/Holdefi/blob/f4df394d7cf6df347b1f1e9af8e2676c5933c2c9/contracts/Holdefi.sol#L429
Type: audit-issue

## Details
Due to the massive factorization of certain behaviors under the same function as addressed in the issue _“\[L08\] Overcomplicated return values”_, the level of indirection present severely degrades the readability of the code.

To give an example, if a liquidator calls [the liquidateBorrowerCollateral function](https://github.com/holdefi/Holdefi/blob/f4df394d7cf6df347b1f1e9af8e2676c5933c2c9/contracts/Holdefi.sol#L429) of the `Holdefi` contract, that same transaction would end up triggering a call to [the clearDebts function](https://github.com/holdefi/Holdefi/blob/f4df394d7cf6df347b1f1e9af8e2676c5933c2c9/contracts/Holdefi.sol#L403), which then would call [the updateSupplyIndex function](https://github.com/holdefi/Holdefi/blob/f4df394d7cf6df347b1f1e9af8e2676c5933c2c9/contracts/Holdefi.sol#L550), which would call afterwards [the getCurrentInterestIndex function](https://github.com/holdefi/Holdefi/blob/f4df394d7cf6df347b1f1e9af8e2676c5933c2c9/contracts/Holdefi.sol#L507), and finally jump to the `HoldefiSettings` contract to call [the getInterests function](https://github.com/holdefi/Holdefi/blob/f4df394d7cf6df347b1f1e9af8e2676c5933c2c9/contracts/HoldefiSettings.sol#L100).

Right after the `updateSupplyIndex` call ends, [the updatePromotionReserve](https://github.com/holdefi/Holdefi/blob/f4df394d7cf6df347b1f1e9af8e2676c5933c2c9/contracts/Holdefi.sol#L569) would be called, which would call [the getCurrentPromotion function](https://github.com/holdefi/Holdefi/blob/f4df394d7cf6df347b1f1e9af8e2676c5933c2c9/contracts/Holdefi.sol#L525), and would end up jumping again to the `HoldefiSettings` contract to call [the getInterests function](https://github.com/holdefi/Holdefi/blob/f4df394d7cf6df347b1f1e9af8e2676c5933c2c9/contracts/HoldefiSettings.sol#L100).

Note that the example of excessive indirection mentioned above is not the only one triggered by the `liquidateBorrowerCollateral` function, but just one of many.

While this does not pose a security risk per se, it introduces a lot of complexity to important sections of the code, is error prone and difficult to maintain in the long term.

Consider reducing excessive indirections throughout the code base by simplifying each function, so that they can fulfill one single and clear purpose, and also avoid over-factorizing behaviors in order to improve the readability and maintenance of the project. If there is a reason or limitation that forces this complexity, consider documenting it in the code.

**Update**: _Not fixed. Holdefi’s statement for this issue:_

> As you mentioned, this does not pose a security risk per se. And it’s not a medium severity issue. It’s just a suggestion.  
> Also, we can use the limited number of values in each function. If we want to simplify functions, we are faced with this error: Stack too deep, try removing local variables.

_We have updated our suggestion to make it clearer._
