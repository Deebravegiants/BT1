# [M] raw_call `value=` kwargs not disabled for static and delegate calls

## Summary
Severity: Medium
Chain: Vyper
Component: vyperlang/vyper
CVE: CVE-2024-24567
Published: 2024-01-30
Source: https://github.com/vyperlang/vyper/security/advisories/GHSA-x2c2-q32w-4w6m
Type: github-advisory

## Details
### Summary
Vyper compiler allows passing a value in builtin `raw_call` even if the call is a `delegatecall` or a `staticcall`. But in the context of `delegatecall` and `staticcall` the handling of value is not possible due to the semantics of the respective opcodes, and vyper will silently ignore the `value=` argument.

A contract search was performed and no vulnerable contracts were found in production.

### Details
The IR for `raw_call` is built in the `RawCall` class:
https://github.com/vyperlang/vyper/blob/9136169468f317a53b4e7448389aa315f90b95ba/vyper/builtins/functions.py#L1100

However, the compiler doesn't validate that if either `delegatecall` or `staticall` are provided as kwargs, that `value` wasn't set. For example, the following compiles without errors:
```python
raw_call(self, call_data2, max_outsize=255, is_delegate_call=True, value=msg.value/2)
```

### Impact
If the semantics of the EVM are unknown to the developer, he could suspect that by specifying the `value` kwarg, exactly the given amount will be sent along to the target. However in fact, no `value` will be sent.

Here is an example of an potentially problematic implementation of multicall utilizing the `raw_call` built-in:
```python
value_accumulator: uint256 = empty(uint256)
    results: DynArray[Result, max_value(uint8)] = []
    return_data: Bytes[max_value(uint8)] = b""
    success: bool = empty(bool)
    for batch in data:
        msg_value: uint256 = batch.value
        value_accumulator = unsafe_add(value_accumulator, msg_value)
        if (batch.allow_failure == False):
            return_data = raw_call(self, batch.call_data, max_outsize=255, value=msg_value, is_delegate_call=True)
            success = True
            results.append(Result({success: success, return_data: return_data}))
        else:
            success, return_data = \
                raw_call(self, batch.call_data, max_outsize=255, value=msg_value, is_delegate_call=True, revert_on_failure=False)
            results.append(Result({success: success, return_data: return_data}))
    assert msg.value == value_accumulator, "Multicall: value mismatch"
    return results
```


_Trimmed to 38 lines — full report: https://github.com/vyperlang/vyper/security/advisories/GHSA-x2c2-q32w-4w6m_
