# [H] Vyper vulnerable to memory corruption in certain builtins utilizing `msize`

## Summary
Severity: High
Chain: Vyper
Component: vyper
CVE: CVE-2023-42443
CWE: Out-of-bounds Write
Published: 2023-09-20
Source: https://github.com/advisories/GHSA-c647-pxm2-c52w
Type: github-advisory

## Details
### Impact
In certain conditions, the memory used by the builtins `raw_call`, `create_from_blueprint` and `create_copy_of` can be corrupted.

- For `raw_call`, the argument buffer of the call can be corrupted, leading to incorrect `calldata` in the sub-context.
- For  `create_from_blueprint` and `create_copy_of`, the buffer for the to-be-deployed bytecode can be corrupted, leading to deploying incorrect bytecode.

Below are the conditions that must be fulfilled for the corruption to happen for each builtin:

#### `raw_call`
- memory is not fully initialized, ex. all parameters to an external function live in calldata
and
- The `data` argument of the builtin is `msg.data`.
and
- The `to`, `value` or `gas` passed to the builtin is some complex expression that results in writing to uninitialized memory (e.g. calling an internal function)

#### `create_copy_of`
- memory is not fully initialized, ex. all parameters to an external function live in calldata
and
- The `value` or `salt` passed to the builtin is some complex expression that results in writing to  uninitialized memory (e.g. calling an internal function)

#### `create_from_blueprint`
- memory is not fully initialized, ex. all parameters to an external function live in calldata
and
- Either no constructor parameters are passed to the builtin or `raw_args` is set to True.
and
- The `value` or `salt` passed to the builtin is some complex expression that results in writing to uninitialized memory (e.g. calling an internal function)

Note: When the builtin is being called from an `internal` function `f` from a function `g`, the issue is not present provided that `g` has written to memory before calling `f`.
 
#### Examples


##### `raw_call`

In the following contract, calling `bar(1,1)` will return:

``` Python
ae42e95100000000000000000000000000000000000000000000000000000000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff00000001
```

_Trimmed to 38 lines — full report: https://github.com/advisories/GHSA-c647-pxm2-c52w_
