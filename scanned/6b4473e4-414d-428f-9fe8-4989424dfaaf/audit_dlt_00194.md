# [H] Improper Initialization in OpenZeppelin

## Summary
Severity: High
Chain: Solidity
Component: @openzeppelin/contracts
CVE: CVE-2021-46320
CWE: Improper Initialization
Published: 2022-02-05
Source: https://github.com/advisories/GHSA-88g8-f5mf-f5rj
Type: github-advisory

## Details
In OpenZeppelin <=v4.4.0, initializer functions that are invoked separate from contract creation (the most prominent example being minimal proxies) may be reentered if they make an untrusted non-view external call. Once an initializer has finished running it can never be re-executed. However, an exception put in place to support multiple inheritance made reentrancy possible, breaking the expectation that there is a single execution.
