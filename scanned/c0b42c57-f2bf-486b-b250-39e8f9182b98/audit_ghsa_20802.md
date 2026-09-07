# [H] linked_list_allocator vulnerable to out-of-bound writes on `Heap` initialization and `Heap::extend`

## Summary
Severity: High
Advisory: GHSA-xg8p-34w2-j49j
CVE: CVE-2022-36086
CWE: CWE-119, CWE-1284
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-xg8p-34w2-j49j
Type: github-advisory

## Affected
- crates.io: `linked_list_allocator` — affected >=0 <0.10.2

## Details
## Impact
_What kind of vulnerability is it? Who is impacted?_

This vulnerability impacts all the initialization functions on the `Heap` and `LockedHeap` types, including `Heap::new`, `Heap::init`, `Heap::init_from_slice`, and `LockedHeap::new`. It also affects multiple uses of the `Heap::extend` method.

### Initialization Functions

The heap initialization methods were missing a minimum size check for the given heap size argument. This could lead to **_out-of-bound writes_** when a heap was initialized with a size smaller than `3 * size_of::<usize>` because of metadata write operations.

### `Heap::extend`

This vulnerability impacts three specific uses of the `Heap::extend` method:

- When calling `Heap::extend` with a size smaller than two `usize`s (e.g., 16 on `x86_64`), the size was erroneously rounded up to the minimum size, which could result in an **_out-of-bounds write_**.
- Calling `Heap::extend` on an empty heap tried to construct a heap starting at address 0, which is also an **_out-of-bounds write_**.
  - One specific way to trigger this accidentally is to call `Heap::new` (or a similar constructor) with a heap size that is smaller than two `usize`s. This was treated as an empty heap as well.
- Calling `Heap::extend` on a heap whose size is not a multiple of the size of two `usize`s resulted in _unaligned writes_. It also left the heap in an unexpected state, which might lead to subsequent issues. We did not find a way to exploit this undefined behavior yet (apart from DoS on platforms that fault on unaligned writes).

## Patches
_Has the problem been patched? What versions should users upgrade to?_

We published a patch in version `0.10.2` and recommend all users to upgrade to it. This patch release includes the following changes:

- The initialization functions now panic if the given size is not large enough to store the necessary metadata. Depending on the alignment of the heap bottom pointer, the minimum size is between `2 * size_of::<usize>` and `3 * size_of::<usize>`.
- The `extend` method now panics when trying to extend an unitialized heap.
- Extend calls with a size smaller than `size_of::<usize>() * 2` are now buffered internally and not added to the list directly. The buffered region will be merged with future `extend` calls.
- The `size()` method now returns the _usable_ size of the heap, which might be slightly smaller than the `top() - bottom()` difference because of alignment constraints.

## Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

To avoid this issue, ensure that the heap is only initialized with a size larger than `3 * size_of::<usize>` and that the `Heap::extend` method is only called with sizes larger than `2 * size_of::<usize>()`. Also, ensure that the total heap size is (and stays) a multiple of `2 * size_of::<usize>()`.

## For more information

If you have any questions or comments about this advisory:
* Open an issue in this repository
* Email @phil-opp at [security@phil-opp.com](mailto:security@phil-opp.com)

## Acknowledgements

This issue was responsibly reported by Evan Richter at ForAllSecure and found with [Mayhem](https://forallsecure.com/mayhem-for-code) and [cargo fuzz](https://github.com/rust-fuzz/cargo-fuzz).

## References
- https://github.com/rust-osdev/linked-list-allocator/security/advisories/GHSA-xg8p-34w2-j49j
- https://nvd.nist.gov/vuln/detail/CVE-2022-36086
- https://github.com/rust-osdev/linked-list-allocator/commit/013b0758643943e8df5b17bbb495460ff47e8bbf
- https://github.com/advisories/GHSA-xg8p-34w2-j49j
- https://github.com/rust-osdev/linked-list-allocator
- https://rustsec.org/advisories/RUSTSEC-2022-0063.html
