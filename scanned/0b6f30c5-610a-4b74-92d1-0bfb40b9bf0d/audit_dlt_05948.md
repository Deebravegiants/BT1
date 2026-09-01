# [?] Merge pull request from GHSA-3p37-3636-q8wv

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2023-05-11
Source: https://github.com/vyperlang/vyper/commit/4f8289a81206f767df1900ac48f485d90fc87edb
Type: security-commit

## Details
Merge pull request from GHSA-3p37-3636-q8wv

in dynarray_make_setter, the length is copied before the data. when the
dst and src arrays do not overlap, this is not a problem. however, when
the dst and src are the same dynarray, this can lead to a
store-before-load, leading any array bounds checks on the right hand
side to function incorrectly. here is an example:

```vyper
@external
def should_revert() -> DynArray[uint256,3]:
    a: DynArray[uint256, 3] = [1, 2, 3]
    a = empty(DynArray[uint256, 3])
    a = [self.a[0], self.a[1], self.a[2]]
    return a  # if bug: returns [1,2,3]
```

this commit moves the length store to after the data copy in
dynarray_make_setter. for hygiene, it also moves the length store to
after the data copy in several other routines. I left pop_dyn_array()
unchanged, because moving the routine does not actually perform any data
copy, it just writes the new length (and optionally returns a pointer to
the popped item).
