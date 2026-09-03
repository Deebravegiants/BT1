# [H] Remote denial of service in Hyperledger Fabric Gateway

## Summary
Severity: High
Chain: Hyperledger Fabric
Component: hyperledger/fabric
CVE: CVE-2022-36023
CWE: Improper Input Validation
Published: 2022-08-16
Source: https://github.com/hyperledger/fabric/security/advisories/GHSA-qj6r-fhrc-jj5r
Type: github-advisory

## Details
### Impact
If a gateway client application sends a malformed request to a gateway peer it may crash the peer node.
This fix checks for the malformed gateway request and returns an error to the gateway client.

### Patches
Fixed in v2.4.6.

### Workarounds
None, users must upgrade to v2.4.6.

### References
https://github.com/hyperledger/fabric/releases/tag/v2.4.6

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Fabric](https://github.com/hyperledger/fabric)

### Credits
Thank you to Haosheng Wang of OPPO ZIWU Security Lab for this disclosure.
