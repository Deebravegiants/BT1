# [H] Improper Input Validation in orderer/common/cluster consensus request

## Summary
Severity: High
Chain: Hyperledger Fabric
Component: hyperledger/fabric
CVE: CVE-2022-31121
CWE: Improper Input Validation
Published: 2022-07-07
Source: https://github.com/hyperledger/fabric/security/advisories/GHSA-72x4-cq6r-jp4p
Type: github-advisory

## Details
### Impact
If a consensus client sends a malformed consensus request to an orderer it may crash the orderer node.
This fix checks for the malformed consensus request and returns an error to the consensus client.

### Patches
Fixed in v2.2.7 and v2.4.5.

### Workarounds
None, users must upgrade to v2.2.7 or v2.4.5.

### References
https://github.com/hyperledger/fabric/releases/tag/v2.2.7
https://github.com/hyperledger/fabric/releases/tag/v2.4.5

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Hyperledger Fabric repository](https://github.com/hyperledger/fabric/issues)

### Credits
Thank you to Haosheng Wang of OPPO ZIWU Security Lab for this disclosure.
