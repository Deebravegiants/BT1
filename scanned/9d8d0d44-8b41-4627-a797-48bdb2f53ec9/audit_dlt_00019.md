# [H] Per-transaction O(N^2) HashDoS via hash-bucket collisions in EVM warm-access and EIP-1153 transient-storage tracking

## Summary
Severity: High
Chain: Ethereum
Component: hyperledger/besu
Published: 2026-08-14
Source: https://github.com/besu-eth/besu/security/advisories/GHSA-m2pj-j62h-7jwm
Type: github-advisory

## Details
MessageFrame's per-transaction warm-address, warm-storage, and transient-storage collections were backed by HashSet/HashSet keyed on Address/Bytes32. Both types compute a grindable base-31 hash and never declare Comparable<Self> directly, so HashMap/HashSet bucket treeification never engages — an attacker able to grind many colliding keys could force O(n) bucket walks per insert, turning a linear number of TSTORE/warm-up operations into quadratic work within a single transaction. Fixed by switching these collections to TreeSet/TreeBasedTable, sorted by each key's natural ordering, so insert cost stays bounded regardless of key distribution. Fixed in Besu 26.7.1 by commit adfa98d0132538cc57f02417dc5d804721bccc49 (besu-eth/besu PR #10895).
