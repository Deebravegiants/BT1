# [M] IdMap from_iter may lead to uninitialized memory being freed on drop

## Summary
Severity: Medium
Advisory: GHSA-qq4c-hm99-979m
CWE: CWE-665
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-18
Source: https://github.com/advisories/GHSA-qq4c-hm99-979m
Type: github-advisory

## Affected
- crates.io: `id-map` — affected >=0.1.6 <0.2.2

## Details
Due to a flaw in the constructor `id_map::IdMap::from_iter`, ill-formed objects may be created in which the amount of actually initialized memory is less than what is expected by the fields of `IdMap`. Specifically, the field `ids` is initialized based on the capacity of the vector `values`, which is constructed from the provided iterator. However, the length of this vector may be smaller than its capacity.

In such cases, when the resulting `IdMap` is dropped, its destructor incorrectly assumes that `values` contains `ids.len() == values.capacity()` initialized elements and attempts to iterate over and drop them. This leads to dereferencing and attempting to free uninitialized memory, resulting in undefined behavior and potential segmentation faults.

The bug was fixed in commit `fab6922`, and all unsafe code was removed from the crate.

Note that the maintainer recommends using the following alternatives:
- [slab](https://crates.io/crates/slab)
- [slotmap](https://crates.io/crates/slotmap)

## References
- https://github.com/andrewhickman/id-map/issues/4
- https://github.com/andrewhickman/id-map/commit/fab6922b955b5a2986dfff2ccb341628faec30ed
- https://github.com/andrewhickman/id-map
- https://rustsec.org/advisories/RUSTSEC-2025-0050.html
