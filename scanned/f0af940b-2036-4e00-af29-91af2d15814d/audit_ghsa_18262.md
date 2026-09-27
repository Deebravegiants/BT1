# [H] arenavec has multiple memory corruption vulnerabilities in safe APIs

## Summary
Severity: High
Advisory: GHSA-3632-54q8-m96x
CWE: CWE-122, CWE-415, CWE-822
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-09-02
Source: https://github.com/advisories/GHSA-3632-54q8-m96x
Type: github-advisory

## Affected
- crates.io: `arenavec` — affected >=0

## Details
The crate has the following vulnerabilities:

- The public trait `arenavec::common::AllocHandle` allows the return of raw pointers through its methods `allocate` and `allocate_or_extend`. However, the trait is not marked as unsafe, meaning users of the crate may implement it under the assumption that the library safely handles the returned raw pointers. These raw pointers can later be dereferenced within safe APIs of the crate-such as `arenavec::common::SliceVec::push`-potentially leading to arbitrary memory access.

- The safe API `arenavec::common::SliceVec::reserve` can reach the private function `arenavec::common::allocate_inner`. Incorrect behavior in `allocate_inner` may result in a `SliceVec` with an increased capacity, even though the underlying memory has not actually been expanded. This mismatch between `SliceVec.capacity` and the actual reserved memory can lead to a heap buffer overflow.

- The safe API `arenavec::common::SliceVec::split_off` can duplicate the ownership of the elements in `self` (of type `SliceVec`) if they implement the `Drop` trait. Specifically, when `at == 0`, the method returns a new `SliceVec` with the same length as `self`. Since both `self` and the returned object point to the same heap memory, dropping one will deallocate the shared memory. When the other is subsequently dropped, it will attempt to free the same memory again, resulting in a double free violation.

## References
- https://github.com/ibabushkin/arenavec/issues/4
- https://github.com/ibabushkin/arenavec/issues/5
- https://github.com/ibabushkin/arenavec/issues/6
- https://github.com/ibabushkin/arenavec
- https://rustsec.org/advisories/RUSTSEC-2025-0053.html
