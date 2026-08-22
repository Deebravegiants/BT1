# [H] Earn free DAI interest (inflation) through instant CDP+DSR in one tx

## Summary
Severity: High
Program: BlockDev Sp. Z o.o
Weakness: Business Logic Errors
Reporter: lucash-dev
State: resolved
Disclosed: 2019-08-12T23:44:52.395Z
Source: https://hackerone.com/reports/665798

## Details
## Summary:
The MCD contracts contain different mechanisms for accumulating rates in different
contracts, namely `pot` and `jug` corresponding to the cost of a loan and interest
earned on savings. Because these rates are not synchronised, and depend on the
call to the `drip` method to be calculated, it's possible to game the system
to obtain returns on DAI "savings" that exist only within a transaction.
This means all holders of ETH/gems can costlessly and risklessly earn interest
from the `pot` contract without ever holding DAI for any amount of time.
This leads to inflation of the DAI supply and transfer of value to attackers.

## Detailed Description of the Attack Mechanism

One of the novel features introduced in the MC contracts is the concept of DSR
(DAI Savings Rate) which incentivises investors to hold DAI, by allowing them
to earn interest on DAI deposits in the `pot` contract.
Normally that doesn't result in overall inflation of the DAI supply,
as the only ways of obtaining the DAI to deposit on the "savings account" is by
either acquiring a CDP (Collateralised Debt Position) or buying DAI from someone
else. As repaying a CDP will require an amount of DAI increasing with time, the
overall economic effect is a net increase in DAI value.

In practice, however, both the Stability Fee rates and the DSR rate accrue at discrete
moments in time (rather than continuously), whenever a user calls the method
`drip` on the `jug` or `pot` contracts. As these methods are not synchronised
between the `jug` and `pot` contracts it is possible, by carefully sequencing
method calls to perform a transaction with the following steps:

1. Transform the ETH/token into gem balance, using the `join` contract.
2. Create a CDP urn (vat.frob), obtaining the maximum amount of DAI from the gem balance.
3. Deposit the resulting DAI balance into `pot` (`join` method).
4. Update accumulated DSR rate (`pot.drip`).
5. Withdraw DAI from `pot` (`exit` method), obtaining the DAI deposited in 3 plus
interest.
6. Repay CDP (again, `vat.frob`), getting back the gem balance.
7. Transform back the gem balance into ETH/token.

At first glance the attack might not seem very practical, since there's no way
to guarantee that no other transaction with call `pot.drip` in the same block, and

_Trimmed to 38 lines — full report: https://hackerone.com/reports/665798_
