# [M] OCL-2 | Veriﬁer Conﬁguration Risk-Free Trade

## Summary
Severity: Medium
Contest weight: 0.1635
Dataset id: 19222
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The conﬁguration of the Chainlink VeriﬁerProxy and Veriﬁer contracts pose a non-trivial threat to the
GMX V2 system.
A malicious user may observe any of the following scenarios and leverage them to execute a risk
free trade on the platform:
-
A certain feed used by GMX V2 is deactivated with isDeactivated == true
-
A veriﬁer has been unset with the unsetVeriﬁer function for a particular conﬁgDigest used by
GMX V2
-
A particular conﬁg that corresponds to the conﬁgDigest used by GMX is not active with
isActive == false
In any of the above scenarios a malicious actor is able to submit a market order which is
un-executable during the period where the feedId or conﬁgDigest is deactivated/misconﬁgured. If
market prices move against the trader during this time, the trader can simply cancel their order.
GMX V2 offers no alternative means of execution for these orders until the feedId or conﬁgDigest is
reactivated as they cannot be executed with the regular oracle system and changing the oracle
conﬁguration for the tokens used would take days using the Timelock contract.

## Recommendation
Consider implementing an alternative pathway to provide prices for orders in the event that a feedId
or conﬁgDigest is deactivated or misconﬁgured. Otherwise consider disallowing the creation of
orders that rely on certain feedId’s or conﬁgDigest’s that are currently deactivated.
