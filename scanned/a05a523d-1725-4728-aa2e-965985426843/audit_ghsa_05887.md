# [M] block_buffer: panic corrupts inline buffer position

## Summary
Severity: Medium
Advisory: GHSA-qwgh-2vcv-g2f7
CWE: CWE-119
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-19
Source: https://github.com/advisories/GHSA-qwgh-2vcv-g2f7
Type: github-advisory

## Affected
- crates.io: `block_buffer` — affected >=0 <0.12.1

## Details
### Summary

A caught panic may leave the cursor position of `EagerBuffer` or `ReadBuffer` in a corrupted state; this in turn allows out-of-bounds reads/writes.

### Details & PoC

The following two tests fail miri:

```rust
#[cfg(miri)]
#[test]
fn eager_digest_blocks_panic_corrupts_inline_position() {
    // `EagerBuffer` stores its cursor in the last byte of the internal block.
    // When `digest_blocks` completes a previously partial block, it overwrites
    // that byte with input data before invoking the caller-provided `compress`
    // callback. If the callback panics, safe code can catch the panic and keep
    // using the buffer while its cursor byte no longer satisfies the internal
    // `pos < block_size` invariant. Under Miri this `get_pos` call reaches the
    // `unreachable_unchecked` used for the assumed-valid cursor.
    let mut buf = EagerBuffer::<U4>::new(&[1, 2]);

    let _ = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
        buf.digest_blocks(&[3, 0xff], |_| panic!("simulated compression failure"));
    }));

    let _ = buf.get_pos();
}

#[cfg(miri)]
#[test]
fn read_buffer_generator_panic_corrupts_inline_position() {
    // `ReadBuffer` stores its cursor in `buffer[0]`, but `write_block` gives
    // `gen_block` mutable access to the whole internal block before restoring
    // `buffer[0]` to a valid cursor. If `gen_block` writes an arbitrary first
    // byte and panics, safe code can catch the panic and later observe an
    // invalid cursor. Under Miri this `get_pos` call reaches the
    // `unreachable_unchecked` used for the assumed-valid cursor.
    let mut buf = ReadBuffer::<U4>::default();

    let _ = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
        buf.write_block(
            1,
            |block| {
                block[0] = 0xff;
                panic!("simulated block generation failure");
            },
            |_| {},
        );
    }));

    let _ = buf.get_pos();
}
```

They fail on an `unreachable_unchecked!()` under the invariant for the `pos` to always be within bounds of the block.

### Impact

While the byte that overwrites `pos` may come from untrusted input and is therefore attacker-controlled, this still relies on the surrounding code catching the panic and carrying on, which should be uncommon in practice.

For this to be exploitable, the attacker also needs a way to trigger a panic here; I have not investigated how feasible that is.

### Credits

The issue was discovered by GPT-5.5

## References
- https://github.com/RustCrypto/utils/security/advisories/GHSA-qwgh-2vcv-g2f7
- https://github.com/RustCrypto/utils
- https://github.com/RustCrypto/utils/releases/tag/block-buffer-v0.12.1
