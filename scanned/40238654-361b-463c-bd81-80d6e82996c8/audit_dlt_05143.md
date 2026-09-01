# [?] Fix panic when deserializing `Duration`

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2025-10-24
Source: https://github.com/lightningdevkit/rust-lightning/commit/7b9bde12156f15b4268c53e2b3a7727fab0d10d5
Type: security-commit

## Details
Fix panic when deserializing `Duration`

`Duration::new` adds any nanoseconds in excess of a second to the
second part. This can overflow, however, panicking. In 0.2 we
introduced a few further cases where we store `Duration`s,
specifically some when handling network messages.

Sadly, that introduced a remotely-triggerable crash where someone
can send us, for example, a malicious blinded path context which
can cause us to panic.

Found by the `onion_message` fuzzer
