# [H] Go Ethereum LES protocol implementation vulnerable to Denial of Service

## Summary
Severity: High
Chain: Ethereum
Component: github.com/ethereum/go-ethereum
CVE: CVE-2018-12018
CWE: Improper Validation of Array Index
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-p5gc-957x-gfw9
Type: github-advisory

## Details
The GetBlockHeadersMsg handler in the LES protocol implementation in Go Ethereum (aka geth) before 1.8.11 may lead to an access violation because of an integer signedness error for the array index, which allows attackers to launch a Denial of Service attack by sending a packet with a -1 query.Skip value. The vulnerable remote node would be crashed by such an attack immediately, aka the EPoD (Ethereum Packet of Death) issue.

### Specific Go Packages Affected
github.com/ethereum/go-ethereum/les
