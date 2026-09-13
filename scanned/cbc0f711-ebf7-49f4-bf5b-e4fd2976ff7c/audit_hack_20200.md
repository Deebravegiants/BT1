# [H] 5.2.1 Configuration is crucial (both Nomad and Connext)

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** BridgeFacet.sol#L231-L238, BridgeFacet.sol#L257-L265, BridgeFacet.sol#L271-L276, Router.sol#L37-
L39, XAppConnectionManager.sol#L106-L108, XAppConnectionManager.sol#L115-L
**Description:** The Connext and Nomad protocol rely heavily on configuration parameters. These parameters
are configured during deployment time and are updated afterwards. Configuration errors can have major conse-
quences. Examples of important configurations are:

- BridgeFacet.sol:s.promiseRouter.
- BridgeFacet.sol:s.connextions.
- BridgeFacet.sol:s.approvedSequencers.
- Router.sol:remotes[].
- xAppConnectionManager.sol:home.
- xAppConnectionManager.sol:replicaToDomain[].
- xAppConnectionManager.sol:domainToReplica[].
**Recommendation:** Have rigorous controls when configuring and updating these values.
