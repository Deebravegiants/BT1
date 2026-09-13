# [M] bytestring equality incorrect for Bytes[N<=32]

## Summary
Severity: Medium
Chain: Vyper
Component: vyperlang/vyper
CVE: CVE-2022-24787
Published: 2022-04-02
Source: https://github.com/vyperlang/vyper/security/advisories/GHSA-7vrm-3jc8-5wwm
Type: github-advisory

## Details
### Impact
bytestrings can have dirty bytes in them, resulting in the word-for-word comparison to give incorrect results, e.g.
```vyper
b1: Bytes[32] = b"abcdef"
b1 = slice(b1, 0, 1)
b2: Bytes[32] = b"abcdef"
t: bool = b1 == b2  # incorrectly evaluates to True
```
even without dirty nonzero bytes, because there is no comparison of the length, two bytestrings can compare to equal if one ends with `"\x00"`.
```vyper
b1: Bytes[32] = b"abc\0"
b2: Bytes[32] = b"abc"
t: bool = b1 == b2  # incorrectly evaluates to True
```

### Patches
fixed in https://github.com/vyperlang/vyper/commit/2c73f8352635c0a433423a5b94740de1a118e508
