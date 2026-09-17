# [?] trie/bintrie: fix overflow management in slot key computation (#33951)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2026-03-05
Source: https://github.com/ethereum/go-ethereum/commit/a0fb8102fefd524dcb1ad884f99ad310f7fe4fe2
Type: security-commit

## Details
trie/bintrie: fix overflow management in slot key computation (#33951)

The computation of `MAIN_STORAGE_OFFSET` was incorrect, causing the last
byte of the stem to be dropped. This means that there would be a
collision in the hash computation (at the preimage level, not a hash
collision of course) if two keys were only differing at byte 31.
