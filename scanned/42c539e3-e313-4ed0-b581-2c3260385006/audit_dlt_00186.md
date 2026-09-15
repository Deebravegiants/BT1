# [H] Hyperledger Fabric subject to Denial of Service via non-validated request

## Summary
Severity: High
Chain: Hyperledger Fabric
Component: github.com/hyperledger/fabric
CVE: CVE-2022-35253
CWE: Improper Input Validation, Uncontrolled Resource Consumption
Published: 2022-09-25
Source: https://github.com/advisories/GHSA-9w7j-q3xw-p9vh
Type: github-advisory

## Details
A vulnerability exists in Hyperledger Fabric < 2.4 could allow an attacker to construct a non-validated request that could cause a denial of service attack.  The peer gateway service tries to extract channel and chaincode information from the signed proposal, but it doesn't check the proposal fields for validity. Therefore a malformed proposal might end up crashing the peer service. This issue has been patched in 2.4.6. There are no known workarounds.
