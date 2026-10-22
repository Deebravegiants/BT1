# [H] Configuration is crucial (both Nomad and Connext)

## Summary
Severity: High
Contest weight: 0.1434
Dataset id: 6783
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Connext and Nomad protocol rely heavily on configuration parameters. These parameters are configured during deployment time and are updated afterwards. Configuration errors can have major consequences. Examples of important configurations are:
• BridgeFacet.sol: s.promiseRouter.
• BridgeFacet.sol: s.connextions.
• BridgeFacet.sol: s.approvedSequencers.
• Router.sol: remotes[].
• xAppConnectionManager.sol: home .
• xAppConnectionManager.sol: replicaToDomain[].
• xAppConnectionManager.sol: domainToReplica[].

## Recommendation
Have rigorous controls when configuring and updating these values.
