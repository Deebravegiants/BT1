# [H] incorrect storage layout for contracts containing large arrays

## Summary
Severity: High
Chain: Vyper
Component: vyperlang/vyper
CVE: CVE-2023-46247
Published: 2023-12-12
Source: https://github.com/vyperlang/vyper/security/advisories/GHSA-6m97-7527-mh74
Type: github-advisory

## Details
### Impact
contracts containing large arrays might underallocate the number of slots they need. prior to v0.3.8, the calculation to determine how many slots a storage variable needed used `math.ceil(type_.size_in_bytes / 32)`:

https://github.com/vyperlang/vyper/blob/6020b8bbf66b062d299d87bc7e4eddc4c9d1c157/vyper/semantics/validation/data_positions.py#L197

the intermediate floating point step can produce a rounding error if there are enough bits set in the IEEE-754 mantissa. roughly speaking, if `type_.size_in_bytes` is large (> 2**46), and slightly less than a power of 2, the calculation can overestimate how many slots are needed. if `type_.size_in_bytes` is slightly more than a power of 2, the calculation can underestimate how many slots are needed.

the following two example contracts can result in overwriting of the variable `vulnerable`:
```vyper
large_array: address[2**64 + 1]  # type_.size_in_bytes == 32 * (2**64 + 1); math.ceil(type_.size_in_bytes / 32) < 2**64 + 1
vulnerable: uint256

# writing to self.large_array[2**64] will overwrite self.vulnerable
```
```vyper
large_dynarray: DynArray[address, 2**64]  # Dynarray has a length word in front, its size in bytes is 32 * (2**64 + 1)
vulnerable: uint256

# writing to self.large_dynarray[2**64 - 1] will overwrite self.vulnerable
```

note that in the latter case, the risk of `vulnerable` being overwritten is relatively small, since it would cost roughly $1.45 million trillion USD at today's gas prices (gas price 20gwei, ETH ~= $1800) in order to extend the DynArray to its full container size.

### Patches
patched by v0.3.8, specifically in commit https://github.com/vyperlang/vyper/commit/0bb7203b584e771b23536ba065a6efda457161bb.

### Workarounds

### References
_Are there any links users can visit to find out more?_
