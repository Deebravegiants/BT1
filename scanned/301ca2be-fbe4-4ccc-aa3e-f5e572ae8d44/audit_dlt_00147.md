# [H] Bounds check on built-in `slice()` function can be overflowed

## Summary
Severity: High
Chain: Vyper
Component: vyperlang/vyper
CVE: CVE-2024-24561
Published: 2024-01-31
Source: https://github.com/vyperlang/vyper/security/advisories/GHSA-9x7f-gwxq-6f2c
Type: github-advisory

## Details
## Summary

[The bounds check for slices](https://github.com/vyperlang/vyper/blob/b01cd686aa567b32498fefd76bd96b0597c6f099/vyper/builtins/functions.py#L404-L457) does not account for the ability for `start + length` to overflow when the values aren't literals. 

If a `slice()` function uses a non-literal argument for the `start`  or `length` variable, this creates the ability for an attacker to overflow the bounds check. 

This issue can be used to do OOB access to storage, memory or calldata addresses. It can also be used to corrupt the `length` slot of the respective array.

A contract search was performed and no vulnerable contracts were found in production.

tracking in issue https://github.com/vyperlang/vyper/issues/3756.
patched in https://github.com/vyperlang/vyper/pull/3818.

## Details
Here the flow for `storage` is supposed, but it is generalizable also for the other locations.

When calling `slice()` on a storage value, there are compile time bounds checks if the `start` and `length` values are literals, but of course this cannot happen if they are passed values:

```python
if not is_adhoc_slice:
    if length_literal is not None:
        if length_literal < 1:
            raise ArgumentException("Length cannot be less than 1", length_expr)

        if length_literal > arg_type.length:
            raise ArgumentException(f"slice out of bounds for {arg_type}", length_expr)

    if start_literal is not None:
        if start_literal > arg_type.length:
            raise ArgumentException(f"slice out of bounds for {arg_type}", start_expr)
        if length_literal is not None and start_literal + length_literal > arg_type.length:
            raise ArgumentException(f"slice out of bounds for {arg_type}", node)
```

At runtime, we perform the following equivalent check, but the runtime check does not account for overflows:
```python
["assert", ["le", ["add", start, length], src_len]],  # bounds check
```

_Trimmed to 38 lines — full report: https://github.com/vyperlang/vyper/security/advisories/GHSA-9x7f-gwxq-6f2c_
