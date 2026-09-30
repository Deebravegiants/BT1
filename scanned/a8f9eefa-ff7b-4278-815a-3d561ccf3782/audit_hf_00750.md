# [C] C-01 | New Resolver Loses Bond After Council Reset

## Summary
Severity: Critical
Contest weight: 0.2768
Dataset id: 2310
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the sendResolverBondToMarket function, the resolver bond is currently stored using:
marketBond[_market].resolverBond = _amount;
This approach overwrites any existing resolver bond, which is generally acceptable as only one
resolution is expected.
However, an issue arises when a market status is resetByCouncil. Here’s the problematic sequence:
1. Reset State: The council votes to reset the market, leaving the previous resolver's bond intact but
not immediately returned.
2. New Proposal: A new resolver proposes a resolution, adding their bond via
sendResolverBondToMarket.
3. Bond Overwrite: The resolverBond value is overwritten with the new bond, effectively discarding
the previous bond value.
4. Loss of Funds: When the previous bond is sent to the disputor (to punish original resolver), the
resolverBond is reset to zero, causing the new resolver to lose their bond.

## Proof of Concept
https://github.com/GuardianAudits/truth-markets-2/blob/6e2fbada7fd14cf0b8106b9b813f2d0caaef9e93/test/Guardian/poc_resolve_bond_lost.t.sol#L347

## Recommendation
To handle the situation where multiple bonds coexist during a reset, the resolver bonds should be
stored incrementally and decremented appropriately when withdrawn or refunded.
Modify sendResolverBondToMarket to increment the value by the new bond amount:
marketBond[_market].resolverBond += _amount.
Similarly, in sendBondFromMarketToSafeBox and issueBondsBackToResolver, decrement the
resolver bond by the transferred amount instead of setting it to zero.
