# [M] 7.2 Dirt Remains After Bad Auction

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected

As described in MIP45c4, the Hole/ ilk.hole values define a global / per-collateral limit of the total
amount of DAI needed to cover the summed debt and liquidation penalty associated with all active
auctions.

The current debt is tracked by the global Dirt and the per collateral ilk.dirt variables.

Upon auction initiation, the tab, the new debt of the system is added to the corresponding variables.
Upon buying from an auction, the owe amount, the amount of debt paid, is removed from the
corresponding variables.

The expected behavior is only loosely covered in MIP45c8:

```
Lastly, various values are updated to record the changed state
of the auction: the DAI needed to cover debt and fees for outstanding
auctions, and outstanding auctions of the given collateral type, are
reduced (via a callback to the liquidator contract) is reduced by owe,
and the tab (DAI collection target) and lot (collateral for sale) of
the auction are adjusted as well. If all collateral has been drained
from an auction, all its data is cleared and it is removed from the
active auctions list. If collateral remains, but the DAI collection
target has been reached, the same is done and excess collateral is
returned to the liquidated Vault.
```
As described in the specification above, the code only removes the received amount of DAI (owe) from
the debt. This works as expected when the auction managed to cover the tab. In this case all debt added
to the dirt during liquidation is removed. During exceptional circumstances however, the situation that
an auction is unable to collect enough DAI to cover the tab despite selling all collateral may arise. In this
scenario the auction terminates but the unrecovered debt amount remains in the dirt variables.

The expected behaviour in this scenario should be documented.

After such an auction, the value of Dirt will exceed the summed debt of all active auctions and it is no
longer possible for the summed debt of all auctions to reach the limit defined by Hole.

If this happens repeatedly, e.g. during a rapid market crash the accumulated unaccounted dirt may
severely restricts the amount of active auctions possible. Most notably this will impact less liquid
collateral types with a comparatively low amount set for ilk.hole.

Code corrected:

The code has been updated and now handles this case correctly: When an auction has sold all collateral
(lot reduced to 0 ) the remaining tab is removed in addition to owe which is the aumount of DAI just
collected:

```
// Removes Dai out for liquidation from accumulator
dog_.digs(ilk, lot == 0? tab + owe : owe);
```
