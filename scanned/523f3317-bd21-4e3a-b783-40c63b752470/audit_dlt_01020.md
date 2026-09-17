# [M] Content Censorship in the InterPlanetary File System (IPFS) via Kademlia DHT abuse

## Summary
Severity: Medium
Chain: github.com/libp2p/go-libp2p-kad-dht
Component: github.com/libp2p/go-libp2p-kad-dht
CVE: CVE-2023-26248
CWE: Cross-Site Request Forgery (CSRF)
Published: 2024-10-25
Source: https://github.com/advisories/GHSA-mqr9-hjr8-2m9w
Type: github-advisory

## Details
The Kademlia DHT (go-libp2p-kad-dht 0.20.0 and earlier) used in IPFS (0.18.1 and earlier) assigns routing information for content (i.e., information about who holds the content) to be stored by peers whose peer IDs have a small DHT distance from the content ID. This allows an attacker to censor content by generating many Sybil peers whose peer IDs have a small distance from the content ID, thus hijacking the content resolution process.
