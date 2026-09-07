# [?] fix[codegen]: recursive dynarray oob check (#4091)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2024-06-11
Source: https://github.com/vyperlang/vyper/commit/21f7172274e551c721e9e35ab3c9d8322a2455d0
Type: security-commit

## Details
fix[codegen]: recursive dynarray oob check (#4091)

this commit fixes more edge cases in `abi_decode` dynarray
validation. these are bugs which were missed (or regressions) in
1f6b9433fbd524, which itself was a continuation of eb011367cc769.

there are multiple fixes contained in this commit.

- similar conceptual error as in 1f6b9433fbd524. when the
length word is out-of-bounds and its runtime is value is zero,
`make_setter` does not enter recursion and therefore there is
no oob check. an example payload which demonstrates this is in
`test_nested_invalid_dynarray_head()`. the fix is to check the
size of the static section ("embedded static size") before entering
the recursion, rather than child_type.static_size (which could be
zero). essentially, this checks that the end of the static section is
in bounds, rather than the beginning.

- the fallback case in `complex_make_setter` could be referring to a
tuple of dynamic types, which makes the tuple itself dynamic, so there
needs to be an oob check there as well.

- `static_size()` is more appropriate than `min_size()` for abi payload
validation, because you can have "valid" ABI payloads where the runtime
length of the dynamic section is zero, because the heads in the static
section all point back into the static section. this commit replaces
the `static_size()` check with `min_size()` check, everywhere.

- remove `returndatasize` check in external calls, because it gets
checked anyways during `make_setter` oob checks.

- add a comment clarifying that payloads larger than `size_bound()` get
rejected by `abi_decode` but not calldata decoding.

tests for each case, contributed by @trocher

---------


_Trimmed to 38 lines — full report: https://github.com/vyperlang/vyper/commit/21f7172274e551c721e9e35ab3c9d8322a2455d0_
