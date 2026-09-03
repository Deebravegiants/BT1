# [?] sp-trie: correctly avoid panicking when decoding bad compact proofs (#6502)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/polkadot-sdk
Published: 2024-11-19
Source: https://github.com/paritytech/polkadot-sdk/commit/5e8348f03f49cc32ad48912e186c04b0f1212b16
Type: security-commit

## Details
sp-trie: correctly avoid panicking when decoding bad compact proofs (#6502)

# Description

Opening another PR because I added a test to check for my fix pushed in
#6486 and realized that for some reason I completely forgot how to code
and did not fix the underlying issue, since out-of-bounds indexing could
still happen even with the check I added. This one should fix that and,
as an added bonus, has a simple test used as an integrity check to make
sure future changes don't accidently revert this fix.

Now `sp-trie` should definitely not panic when faced with bad
`CompactProof`s. Sorry about that 😅

This, like #6486, is related to issue #6485

## Integration

No changes have to be done downstream, and as such the version bump
should be minor.

---------

Co-authored-by: Bastian Köcher <git@kchr.de>
