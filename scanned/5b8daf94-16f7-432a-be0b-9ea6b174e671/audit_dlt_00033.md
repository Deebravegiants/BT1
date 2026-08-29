# [H] Witness Block Parsing DoS Vulnerability 

## Summary
Severity: High
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
CVE: CVE-2022-39389
CWE: Improper Input Validation
Published: 2022-11-17
Source: https://github.com/lightningnetwork/lnd/security/advisories/GHSA-hc82-w9v8-83pr
Type: github-advisory

## Details
### Impact

All lnd nodes before version `v0.15.4` are vulnerable to a block parsing bug that can cause a node to enter a degraded state once encountered. In this degraded state, nodes can continue to make payments and forward HTLCs, and close out channels. Opening channels is prohibited, and also on chain transaction events will be undetected. 

This can cause loss of funds if a CSV expiry is researched during a breach attempt or a CLTV delta expires forgetting the funds in the HTLC. 

### Patches

A patch is available starting with lnd `v0.15.4`. 

### Workarounds

Nodes can use the `lncli updatechanpolicy` RPC call to increase their CLTV value to a very high amount or increase their fee policies. This will prevent nodes from routing through your node, meaning that no pending HTLCs can be present. 

### References

https://github.com/lightningnetwork/lnd/issues/7096

https://github.com/lightningnetwork/lnd/releases/tag/v0.15.4-beta
