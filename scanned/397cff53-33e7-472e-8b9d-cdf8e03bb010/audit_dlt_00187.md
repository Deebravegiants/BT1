# [H] NULL Pointer Dereference in HyperLedger Fabric

## Summary
Severity: High
Chain: Hyperledger Fabric
Component: github.com/hyperledger/fabric
CVE: CVE-2021-43667
CWE: NULL Pointer Dereference
Published: 2022-05-25
Source: https://github.com/advisories/GHSA-vjj6-5m9f-wqjw
Type: github-advisory

## Details
A vulnerability has been detected in HyperLedger Fabric v1.4.0, v2.0.0, v2.1.0. This bug can be leveraged by constructing a message whose payload is nil and sending this message with the method 'forwardToLeader'. This bug has been admitted and fixed by the developers of Fabric. If leveraged, any leader node will crash.
