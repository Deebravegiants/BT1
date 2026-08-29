# [H] go-ethereum vulnerable to denial of service via crafted GraphQL query

## Summary
Severity: High
Chain: Ethereum
Component: github.com/ethereum/go-ethereum
CVE: CVE-2023-42319
CWE: Uncontrolled Resource Consumption
Published: 2023-10-18
Source: https://github.com/advisories/GHSA-v9jh-j8px-98vq
Type: github-advisory

## Details
Geth (aka go-ethereum) through 1.13.4, when `--http --graphql` is used, allows remote attackers to cause a denial of service (memory consumption and daemon hang) via a crafted GraphQL query.

NOTE: the vendor's position is that the "graphql endpoint [is not] designed to withstand attacks by hostile clients, nor handle huge amounts of clients/traffic.
