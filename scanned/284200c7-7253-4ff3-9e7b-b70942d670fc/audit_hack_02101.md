# [M] 7.4 Specification Mismatches

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Specification Changed

There are multiple errors of different severity in the MIP45 specification. For each item we list the relevant
part of the specification and the explanation of the error:

- c7: "all liquidations disabled(2): This means no new liquidations (Clipper.kick), no takes
    (Clipper.take), and no redos (Clipper.redo)"
    Reason: While this is correctly implemented, the code comment is a bit unclear as it does not
    specify that no kick invocations are allowed on level 2:

```
// Levels for circuit breaker
// 0: no breaker
// 1: no new kick()
```

```
// 2: no new redo() or take()
```
- c8: "If the auction reached the tail value, ... then the Clipper.take would revert if called"

```
Reason: This description of the tail value mismatches with its description in c1: "Time elapsed
before auction reset". Note that the source code follows c1:
```
```
function status(uint96 tic, uint256 top) internal view returns (bool done, uint256 price) {
price = calc.price(top, sub(block.timestamp, tic));
done = (sub(block.timestamp, tic) > tail || rdiv(price, top) < cusp);
}
```
- c8: "If the auction ... fell by cusp percent of top, then Clipper.take would revert if called, ..."

```
Reason: Discrepancy with c1 "cusp = 0.6 * RAY (60% of the starting price), then the auction will
need to be reset when reaching just below the price of 720." c1 implies that the auction needs to be
restarted once it falls by at least cusp percent, while c8 implies that it needs to be restarted when it
falls by more than cusp percent.
```
- c8: "If the caller provided a bytestring with greater than zero length, an external call is made to the
    who address, assuming it exposes a function, follow Solidity conventions, with the following
    signature."
    Reason: This is not entirely correct, as no call will be made if who is the Dog contract or the Vat
    contract.
- c13: "treats price at the current time as a function of the initial price of an auction and the time at
    which it was initiated".

```
Reason: The price is a function of the initial price and the duration since last redo.
```
- c14: "This process will repeat until all collateral has been sold or the whole debt has been collected"

```
Reason: This is not true as the auction might also be completed through a call to the snip function.
```
- c15: "The Clipper.take call can send any remaining collateral or DAI beyond owe to a cold wallet
    address inaccessible to the keeper."

```
Reason: This statement is slightly imprecise as the remaining collateral or DAI would be moved by
the clipperCallee.
```
- c16: "A mutex check to ensure the Clipper.take function is not already being invoked from
    clipperCallee."
    Reason:. The mutex check prevents reentrancy into Clipper.take/redo() irregardless of the
    clipperCallee.
- c17: "calls dog.digs in order to increment its Hole and ilk.hole values by the remaining auction tab."

```
Reason: It is not Hole/hole that are modified but Dirt/dirt.
```
- c18: "function file(bytes32 what, uint256 data) external"

```
Reason: data should be of the type address.
```
- c18: function active() external view returns (uint256[]);

```
Reason: The automatically created getter active will requires numeric index as a parameter and
returns a single uint256.
```
- c26: "urn.art * ilk.rate * ilk.chop ||"

```
Reason: Missing operator for comparison.
```
- c26: In equations it seems that the units are not taken into account e.g.,
    urn.art * ilk.rate * ilk.chop > room. However, this choice is not explicitly stated which
    creates mismatch with the implementation.


- c26: "vault.art * ilk.rate <= room"
    Reason: Missing chop.
- c27: "if amt < lot && tab - (amt * abacus.price) < ilk.dust"
    Reason: Mismatch with code. The code says amt < lot && owe < tab.

Specification corrected:

The specification has been corrected and matches the code behavior apart from minor diversions that
are irrelevant to general usage, e.g., internal restrictions on callback targets.
