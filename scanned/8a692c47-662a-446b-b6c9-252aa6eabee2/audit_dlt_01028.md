# [H] Access Restriction Bypass in go-ipfs

## Summary
Severity: High
Chain: github.com/ipfs/go-ipfs
Component: github.com/ipfs/go-ipfs
CVE: CVE-2020-10937
CWE: Improper Access Control
Published: 2024-04-24
Source: https://github.com/advisories/GHSA-r23h-3jmw-q7hr
Type: github-advisory

## Details
An issue was discovered in IPFS (aka go-ipfs) 0.4.23. An attacker can generate ephemeral identities (Sybils) and leverage the IPFS connection management reputation system to poison other nodes' routing tables, eclipsing the nodes that are the target of the attack from the rest of the network. Later versions, in particular go-ipfs 0.7, mitigate this.
