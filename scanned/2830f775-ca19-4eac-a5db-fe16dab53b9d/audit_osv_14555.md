# [M] CVE-2019-1010299

## Summary
Severity: Medium
Advisory: CVE-2019-1010299
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-07-15
Source: https://osv.dev/vulnerability/CVE-2019-1010299
Type: osv

## Details
The Rust Programming Language Standard Library 1.18.0 and later is affected by: CWE-200: Information Exposure. The impact is: Contents of uninitialized memory could be printed to string or to log file. The component is: Debug trait implementation for std::collections::vec_deque::Iter. The attack vector is: The program needs to invoke debug printing for iterator over an empty VecDeque. The fixed version is: 1.30.0, nightly versions after commit b85e4cc8fadaabd41da5b9645c08c68b8f89908d.

## References
- https://github.com/rust-lang/rust/issues/53566
- https://github.com/rust-lang/rust/pull/53571/commits/b85e4cc8fadaabd41da5b9645c08c68b8f89908d
