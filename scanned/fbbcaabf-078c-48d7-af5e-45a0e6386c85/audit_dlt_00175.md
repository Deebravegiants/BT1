# [H] Denial of service in go-ethereum

## Summary
Severity: High
Chain: Ethereum
Component: github.com/ethereum/go-ethereum
CVE: CVE-2021-42219
CWE: Uncontrolled Resource Consumption
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-vrcc-g6vj-mh5w
Type: github-advisory

## Details
Go-Ethereum v1.10.9 was discovered to contain an issue which allows attackers to cause a denial of service (DoS) via sending an excessive amount of messages to a node. This is caused by missing memory in the component /ethash/algorithm.go.
