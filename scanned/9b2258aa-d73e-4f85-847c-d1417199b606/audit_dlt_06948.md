# [H] Missing Constraint in default_dict_copy

## Summary
Severity: High
Chain: Smart contract
Component: 2024-09-kakarot
Published: 2024-10-27
Source: https://github.com/code-423n4/2024-09-kakarot-findings/issues/91
Type: code-finding

## Details
# Lines of code

https://github.com/kkrt-labs/kakarot/blob/7411a5520e8a00be6f5243a50c160e66ad285563/src/kakarot/account.cairo#L83
https://github.com/kkrt-labs/kakarot/blob/7411a5520e8a00be6f5243a50c160e66ad285563/src/utils/dict.cairo#L83


# Vulnerability details

### Summary
In CairoZero, the correct usage of dict objects created via `default_dict_new` must be paired with a call to `default_dict_finalize` to ensure the integrity and prevent malicious prover's manipulation of its contents. However, this constraint is missing in the handling of `transient_storage`, `storage` and `valid_jumpdests`, leading to severe vulnerabilities when executing smart contracts.

### Description of the Issue  
According to CairoZero's documentation ([link to default_dict](https://docs.cairo-lang.org/reference/common_library.html#default-dict)), a proper workflow involving `default_dict_new` includes a finalization step using `default_dict_finalize`. This ensures the correct initialization of dictionary elements and prevents malicious provers from manipulating dictionary values through hints. Specifically, `default_dict_finalize` enforces the constraint that the initial value of the first element's `prev_value` in the dictionary must equal to the `default_value`.

However, in the case of `transient_storage`, `storage` and `valid_jumpdests`, this crucial constraint is missing. 

I will illustrate this issue using `transient_storage`. First, `transient_storage` is initialized in `Account.init()` as follows:

```rust
let (transient_storage_start) = default_dict_new(0);
```

However, there is no subsequent call to `default_dict_finalize(transient_storage_start, transient_storage, 0)` to finalize the storage. Instead, the function `default_dict_copy()` is called on `transient_storage` multiple times during a transaction through the `Account.copy()` function:

```rust
let (transient_storage_start, transient_storage) = default_dict_copy(
    self.transient_storage_start, self.transient_storage
);
```

This copy operation starts by calling `dict_squash` on the original `transient_storage`:

```rust
func default_dict_copy{range_check_ptr}(start: DictAccess*, end: DictAccess*) -> (
    DictAccess*, DictAccess*
) {
    alloc_locals;
    let (squashed_start, squashed_end) = dict_squash(start, end);
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-09-kakarot-findings/issues/91_
