# [M] CosmWasm Allows Bypass of Capability Restrictions in Blockchains

## Summary
Severity: Medium
Chain: cosmwasm
Component: cosmwasm
CVE: CVE-2025-25500
CWE: Improper Access Control, Missing Authentication for Critical Function
Published: 2025-03-18
Source: https://github.com/advisories/GHSA-cg8r-jwg7-r2x4
Type: github-advisory

## Details
An issue in CosmWasm prior to v2.2.0 allows attackers to bypass capability restrictions in blockchains by exploiting a lack of runtime capability validation. This allows attackers to deploy a contract without capability enforcement, and execute unauthorized actions on the blockchain.
