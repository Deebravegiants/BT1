# [H] go-merkledag's ProtoNode may be modified such that common method calls may panic

## Summary
Severity: High
Chain: github.com/ipfs/go-merkledag
Component: github.com/ipfs/go-merkledag
CVE: CVE-2022-23495
CWE: Unchecked Return Value, Improper Handling of Exceptional Conditions
Published: 2022-12-08
Source: https://github.com/advisories/GHSA-x39j-h85h-3f46
Type: github-advisory

## Details
### Impact

A `ProtoNode` may be modified in such a way as to cause various encode errors which will trigger a panic on common method calls that don't allow for error returns.

A `ProtoNode` should only be able to encode to valid DAG-PB, attempting to encode invalid DAG-PB forms will result in an error from the codec. Manipulation of an existing (newly created or decoded) `ProtoNode` using the modifier methods did not account for certain states that would place the `ProtoNode` into an unencodeable form.

Due to conformance with the [`github.com/ipfs/go-block-format#Block`](https://pkg.go.dev/github.com/ipfs/go-block-format#Block) and [`github.com/ipfs/go-ipld-format#Node`](https://pkg.go.dev/github.com/ipfs/go-ipld-format#Node) interfaces, certain methods, which internally require a re-encode if state has changed, will panic due to the inability to return an error.

Additionally, use of the `ProtoNode#SetCidBuilder()` method to set a non-functioning `CidBuilder` (such as one that refers to a multihash where an implementation of that hash function is not available) may cause the same methods to panic as a new CID is required but cannot be created.

### Patches

Releases involving fixes for this issue are [v0.8.0](https://github.com/ipfs/go-merkledag/releases/tag/v0.8.0) and [v0.8.1](https://github.com/ipfs/go-merkledag/releases/tag/v0.8.1). The recommended minimum version is **v0.8.1**.

* Additional checks are performed on `ProtoNode` state changes to avoid the possibility of creating unencodeable forms, errors are returned where this is the case.
* The builder passed in to `SetCidBuilder()` is inspected to attempt to determine if it is usable to generate CIDs, otherwise an error is returned.
* The panics have been removed and replaced with default values (empty byte slice for `RawData()` and a default zero-bytes DAG-PB CID for methods involving CIDs).

### Workarounds

These workarounds are available when using impacted versions to avoid panic conditions, and may be generally appropriate in order to provide meaningful feedback to users and avoid generating bad, or unexpected encoded data:

* Sanitise inputs when allowing user-input to set a new `CidBuilder` on a `ProtoNode`.
* Sanitise `Tsize` (`Link#Size`) values such that they are a reasonable byte-size for sub-DAGs where derived from user-input.

### References

* https://github.com/ipfs/kubo/issues/9297
* https://github.com/ipfs/go-merkledag/issues/90
* https://github.com/ipfs/go-merkledag/releases/tag/v0.8.0
* https://github.com/ipfs/go-merkledag/pull/91
* https://github.com/ipfs/go-merkledag/pull/92
* https://github.com/ipfs/go-merkledag/pull/93
* https://github.com/ipfs/go-merkledag/releases/tag/v0.8.1


### Credit


_Trimmed to 38 lines — full report: https://github.com/advisories/GHSA-x39j-h85h-3f46_
