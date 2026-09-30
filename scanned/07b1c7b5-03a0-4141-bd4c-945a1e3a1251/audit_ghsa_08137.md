# [M] bytes has integer overflow in BytesMut::reserve

## Summary
Severity: Medium
Advisory: GHSA-434x-w66g-qw3r
CVE: CVE-2026-25541
CWE: CWE-680
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-434x-w66g-qw3r
Type: github-advisory

## Affected
- crates.io: `bytes` — affected >=1.2.1 <1.11.1

## Details
# Details

In the unique reclaim path of `BytesMut::reserve`, the condition
```rs
if v_capacity >= new_cap + offset
```
uses an unchecked addition. When `new_cap + offset` overflows `usize` in release builds, this condition may incorrectly pass, causing `self.cap` to be set to a value that exceeds the actual allocated capacity. Subsequent APIs such as `spare_capacity_mut()` then trust this corrupted `cap` value and may create out-of-bounds slices, leading to UB.

This behavior is observable in release builds (integer overflow wraps), whereas debug builds panic due to overflow checks.

## PoC

```rs
use bytes::*;

fn main() {
    let mut a = BytesMut::from(&b"hello world"[..]);
    let mut b = a.split_off(5);

    // Ensure b becomes the unique owner of the backing storage
    drop(a);

    // Trigger overflow in new_cap + offset inside reserve
    b.reserve(usize::MAX - 6);

    // This call relies on the corrupted cap and may cause UB & HBO
    b.put_u8(b'h');
}
```

# Workarounds

Users of `BytesMut::reserve` are only affected if integer overflow checks are configured to wrap. When integer overflow is configured to panic, this issue does not apply.

This vulnerability is also known as [RUSTSEC-2026-0007](https://rustsec.org/advisories/RUSTSEC-2026-0007.html).

## References
- https://github.com/tokio-rs/bytes/security/advisories/GHSA-434x-w66g-qw3r
- https://nvd.nist.gov/vuln/detail/CVE-2026-25541
- https://github.com/tokio-rs/bytes/commit/d0293b0e35838123c51ca5dfdf468ecafee4398f
- https://github.com/tokio-rs/bytes
- https://github.com/tokio-rs/bytes/releases/tag/v1.11.1
- https://rustsec.org/advisories/RUSTSEC-2026-0007.html
