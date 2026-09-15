# [M] Go Ethereum allows attackers to use manipulation of time-difference values to achieve replacement of main-chain blocks

## Summary
Severity: Medium
Chain: Ethereum
Component: github.com/ethereum/go-ethereum
CVE: CVE-2022-37450
Published: 2022-08-06
Source: https://github.com/advisories/GHSA-rqmg-hrg4-fm69
Type: github-advisory

## Details
Go Ethereum (aka geth) through 1.10.21 allows attackers to increase rewards by mining blocks in certain situations, and using a manipulation of time-difference values to achieve replacement of main-chain blocks, aka Riskless Uncle Making (RUM), as exploited in the wild in 2020 through 2022.
