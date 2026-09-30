# [H] Authentication bypass by capture-replay in github.com/cosmos/ethermint

## Summary
Severity: High
Chain: github.com/cosmos/ethermint
Component: github.com/cosmos/ethermint
CVE: CVE-2021-25834
CWE: Improper Authentication, Authentication Bypass by Capture-replay
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-93p5-8fqw-wjx3
Type: github-advisory

## Details
Cosmos Network Ethermint <= v0.4.0 is affected by a transaction replay vulnerability in the EVM module. If the victim sends a very large nonce transaction, the attacker can replay the transaction through the application.

### Specific Go Packages Affected
github.com/cosmos/ethermint/rpc/namespaces/eth
