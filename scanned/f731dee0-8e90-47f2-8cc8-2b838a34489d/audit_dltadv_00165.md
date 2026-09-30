# [M] Vyper's `slice()` may elide side-effects when output length is 0

## Summary
Severity: Medium
Advisory: PYSEC-2026-2028
Aliases: CVE-2025-47774, GHSA-3vcg-j39x-cwfm
Package: vyper
Published: 2026-07-07
Source: https://osv.dev/vulnerability/PYSEC-2026-2028
Type: chain-advisory

## Affected
- PyPI: `vyper` — affected 0.1.0b1, 0.1.0b10, 0.1.0b11, 0.1.0b12, 0.1.0b13, 0.1.0b14, 0.1.0b15, 0.1.0b16, 0.1.0b17, 0.1.0b2, 0.1.0b3, 0.1.0b4, 0.1.0b5, 0.1.0b6, 0.1.0b7, 0.1.0b8, 0.1.0b9, 0.2.1, 0.2.10, 0.2.11, 0.2.12, 0.2.13, 0.2.14, 0.2.15, 0.2.16, 0.2.2, 0.2.3, 0.2.4, 0.2.5, 0.2.6, 0.2.7, 0.2.8, 0.2.9, 0.3.0, 0.3.1, 0.3.10, 0.3.10rc1, 0.3.10rc2, 0.3.10rc3, 0.3.10rc4, 0.3.10rc5, 0.3.2, 0.3.3, 0.3.4, 0.3.5, 0.3.6, 0.3.7, 0.3.8, 0.3.9, 0.4.0, 0.4.0b1, 0.4.0b2, 0.4.0b3, 0.4.0b4, 0.4.0b5, 0.4.0b6, 0.4.0rc1, 0.4.0rc2, 0.4.0rc3, 0.4.0rc4, 0.4.0rc5, 0.4.0rc6, 0.4.1, 0.4.1b1, 0.4.1b2, 0.4.1b3, 0.4.1b4, 0.4.1rc1, 0.4.1rc2, 0.4.1rc3, 0.4.2rc1

## Details
### Impact
the `slice()` builtin can elide side effects when the output length is 0, and the source bytestring is a builtin (`msg.data` or `<address>.code`). the reason is that for these source locations, the check that `length >= 1` is skipped:
https://github.com/vyperlang/vyper/blob/68b68c4b30c5ef2f312b4674676170b8a6eaa316/vyper/builtins/functions.py#L315-L319

the result is that a 0-length bytestring constructed with slice can be passed to `make_byte_array_copier`, which elides evaluation of its source argument when the max length is 0:
https://github.com/vyperlang/vyper/blob/68b68c4b30c5ef2f312b4674676170b8a6eaa316/vyper/codegen/core.py#L189-L191

the impact is that side effects in the `start` argument may be elided when the `length` argument is 0, e.g. `slice(msg.data, self.do_side_effect(), 0)`.

the following example illustrates how the issue would look in user code
```vyper
counter: public(uint256)

@external
def test() -> Bytes[10]:
    b: Bytes[10] = slice(msg.data, self.side_effect(), 0)
    return b

def side_effect() -> uint256:
    self.counter += 1
    return 0
```

the severity assigned is low, since this is not a very useful pattern and unlikely to be found in user code.

### Patches

the fix is tracked in https://github.com/vyperlang/vyper/pull/4645, which disallows any invocation of `slice()` with length 0, including for the ad hoc locations discussed in this advisory.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

### References
_Are there any links users can visit to find out more?_

## References
- https://github.com/vyperlang/vyper/security/advisories/GHSA-3vcg-j39x-cwfm
- https://nvd.nist.gov/vuln/detail/CVE-2025-47774
- https://github.com/vyperlang/vyper/pull/4645
- https://github.com/vyperlang/vyper
- https://github.com/vyperlang/vyper/blob/68b68c4b30c5ef2f312b4674676170b8a6eaa316/vyper/builtins/functions.py#L315-L319
- https://github.com/vyperlang/vyper/blob/68b68c4b30c5ef2f312b4674676170b8a6eaa316/vyper/codegen/core.py#L189-L191
- https://pypi.org/project/vyper
- https://github.com/advisories/GHSA-3vcg-j39x-cwfm
