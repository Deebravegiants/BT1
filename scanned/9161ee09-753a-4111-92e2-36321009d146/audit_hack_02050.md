# [M] 5.1 Funds Can Avoid Paying Protocol Fees

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Acknowledged

Consider a fund that has not enabled autoProtocolFeeSharesBuyback and assume that over time
the protocol fee reserve has accrued a sizeable amount of shares of this fund.

The fund, through its manager, can avoid paying protocol fees by employing the following vector:

```
1.Move all assets of the vault to an external position. Currently, with only the
CompoundDebtPosition available as an external position, this means exchanging all of the
vaults holdings into a cToken and transferring it to the external position.
2.Remove the external position. Note that, at this point, the GAV of the fund is close to 0.
3.Call buyBackProtocolFeeShares which calculates a really low price per share. This means
that only a small amount of MLN tokens needs to be burnt to burn the protocol fee shares and,
thus, pay back the fee.
4.Reactivate the external position and move the funds back.
```
Note that a similar vector can be used by the fund manager to avoid minting protocol fees while migrating
or reconfiguration the fund.

The opportunistic behavior of the manager against the users of the fund is well documented. However,
adversarial actions against the protocol are not mentioned.

Note that the underlying problem, a manipulated lower GAV due to hiding assets of the fund in a removed
external position can also be abused by the fund manager to buy shares for a low price.

Acknowledged:


Avantgarde Finance responded:

```
As the audit team importantly noted, this issue only potentially affects the protocol fee amount
ultimately burned, and does not impact end users of the protocol. Hence, rather than changing the
core contracts for this release to protect against the reported deviant behavior, we have decided to
combine the monitoring of blatant protocol fee violations with potential on- and off-chain penalties.
```
```
Deviant behavior can monitored off-chain by comparing each shares buyback event with the last
known share price.
If the Council assesses that there is a blatant attempt to evade protocol fees, it would be possible, for
example, to restrict buying back shares by upgrading the ProtocolFeeReserveProxy contract to
disallow particular funds.
```
```
We can reevaluate for subsequent releases whether or not to prevent this behavior at the core
protocol level.
```
