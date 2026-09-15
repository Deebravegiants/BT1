# [H] 7.4 Untracked Bad Debt / System Health

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design High Version 1 Code Corrected

A stablemarket attempts to keep the equilibrium between the positions of stable seekers and hedging
agents. At times the attempt to keep the equilibrium may not be successful:

- Should they price of a collateral decrease too fast and keepers can't or don't forcefully cash out bad
    perpetuals in time, the situation arises where the collateral put up by the perpetual evaluated at the
    current rate can no longer cover its committed amount at the rate the perpetual has been created. In
    this case the perpetual is liquidated leaving bad debt to the system.

Should the collateral of the stablecoin not be fully covered at all times (This means the collateral brought
by stable seekers equals the amount covered by the hedging agents), 2 kinds of bad debt can occur:

- Coverage of the collateral is less than 100% and the price of the collateral decreases from x to y:

For the uncovered collateral stablecoins have been minted a the higher collateral price x. Now the value
of the collateral dropped to y. The minted stablecoins are now only partially covered by the value of the
collateral. Note that should a new Hedging Agent now enter the system and covers some more of the
collateral, this is done at the current exchange rate, not the rate used to mint the stablecoin. At this point
the virtual loss of the system is converted into actual bad debt of the system.

Vice versa, should the price of uncovered collateral increase the system makes a profit.

- Coverage of the collateral is more than 100% and the price of a collateral increases.

(Note that this cannot happen if maxALock is set to less than 100%)

Here profits made by Hedging Agents would exceed the increase in value of the collateral held by the
system to back the minted stablecoins. This loss is taken by the system.

Overall bad debt is neither tracked nor handled otherwise. If possible it could be accounted for and
compared with what is currently called "system surplus" which includes the fees collected and other gains
made by the system.

No functionality to query the health of the system exist. Such information however is vital for all users
investing funds into the system.


Code corrected:

The new stocksUsers enables to keep better track of the current system health and the bad debt.
However, these computations need to be performed off-chain, e.g., in the front-end. For more information
see the description of System Accounting.
