# [M] 5.2.12RootManager.propagatedoes not operate in a fail-safe manner

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** RootManager.sol#L147-L173
**Description:** A bridge failure on one of the supported chains will cause the entire messaging network to break
down.
When theRootManager.propagatefunction is called, it will loop through the hub connector of all six chains (Ar-
bitrum, Gnosis, Multichain, Optimism, Polygon, ZKSync) and attempt to send over the latest aggregated root by
making a function call to the respective chain's AMB contract. There is a tight dependency between the chain's
AMB and hub connector.
The problem is that if one of the function calls to the chain's AMB contract reverts (e.g. one of the bridges is
paused), the entireRootManager.propagatefunction will revert, and the messaging network will stop working until
someone figure out the problem and manually removes the problematic hub connector.
As Connext grows, the number of chains supported will increase, and the risk of this issue occurring will also
increase.
**Recommendation:** TheRootManager.propagatefunction should operate in a fail-safe manner (e.g. using try-
catch or address.call). Chain's AMB contracts are considered external third-party and beyond Connext control.
Thus, theRootManager.propagatefunction should not assume that function calls to these third-party bridge con-
tracts will always succeed and will not revert.
**Connext:** Solved in PR 2430.
**Spearbit:** Verified.
