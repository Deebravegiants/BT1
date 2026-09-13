# [H] Incorrect Comparison in Vyper

## Summary
Severity: High
Advisory: GHSA-7vrm-3jc8-5wwm
CWE: CWE-697
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-04-04
Source: https://github.com/advisories/GHSA-7vrm-3jc8-5wwm
Type: github-advisory

## Affected
- PyPI: `vyper` — affected >=0 <0.3.2

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

## References
- https://github.com/vyperlang/vyper/security/advisories/GHSA-7vrm-3jc8-5wwm
- https://github.com/vyperlang/vyper/commit/2c73f8352635c0a433423a5b94740de1a118e508
- https://github.com/pypa/advisory-database/tree/main/vulns/vyper/PYSEC-2022-196.yaml
- https://github.com/vyperlang/vyper
