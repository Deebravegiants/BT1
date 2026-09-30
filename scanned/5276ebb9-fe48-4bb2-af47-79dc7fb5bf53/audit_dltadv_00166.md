# [M] Vyper's `concat()` builtin may elide side-effects for zero-length arguments

## Summary
Severity: Medium
Advisory: PYSEC-2026-2029
Aliases: CVE-2025-47285, GHSA-qhr6-mgqr-mchm
Package: vyper
Published: 2026-07-07
Source: https://osv.dev/vulnerability/PYSEC-2026-2029
Type: chain-advisory

## Affected
- PyPI: `vyper` — affected 0.1.0b1, 0.1.0b10, 0.1.0b11, 0.1.0b12, 0.1.0b13, 0.1.0b14, 0.1.0b15, 0.1.0b16, 0.1.0b17, 0.1.0b2, 0.1.0b3, 0.1.0b4, 0.1.0b5, 0.1.0b6, 0.1.0b7, 0.1.0b8, 0.1.0b9, 0.2.1, 0.2.10, 0.2.11, 0.2.12, 0.2.13, 0.2.14, 0.2.15, 0.2.16, 0.2.2, 0.2.3, 0.2.4, 0.2.5, 0.2.6, 0.2.7, 0.2.8, 0.2.9, 0.3.0, 0.3.1, 0.3.10, 0.3.10rc1, 0.3.10rc2, 0.3.10rc3, 0.3.10rc4, 0.3.10rc5, 0.3.2, 0.3.3, 0.3.4, 0.3.5, 0.3.6, 0.3.7, 0.3.8, 0.3.9, 0.4.0, 0.4.0b1, 0.4.0b2, 0.4.0b3, 0.4.0b4, 0.4.0b5, 0.4.0b6, 0.4.0rc1, 0.4.0rc2, 0.4.0rc3, 0.4.0rc4, 0.4.0rc5, 0.4.0rc6, 0.4.1, 0.4.1b1, 0.4.1b2, 0.4.1b3, 0.4.1b4, 0.4.1rc1, 0.4.1rc2, 0.4.1rc3, 0.4.2rc1

## Details
### Impact
`concat()` may skip evaluation of side effects when the length of an argument is zero. this is due to a fastpath in the implementation which skips evaluation of argument expressions when their length is zero:
https://github.com/vyperlang/vyper/blob/68b68c4b30c5ef2f312b4674676170b8a6eaa316/vyper/builtins/functions.py#L560-L562

in practice, it would be very unusual in user code to construct zero-length bytestrings using an expression with side-effects, since zero-length bytestrings are typically constructed with the empty literal `b""`; the only way to construct an empty bytestring which has side effects would be with the ternary operator introduced in v0.3.8, e.g. `b"" if self.do_some_side_effect() else b""`.

the following example demonstrates how the issue would look in user code
```vyper
counter: public(uint256)

@external
def test() -> Bytes[256]:
    a: Bytes[256] = concat(b"" if self.sideeffect() else b"", b"aaaa")
    return a

def sideeffect() -> bool:
    self.counter += 1
    return True
```

the severity assigned is low, since, as mentioned, this would be a very unusual pattern in user-code.

### Patches

fix is tracked in https://github.com/vyperlang/vyper/pull/4644

### Workarounds
don't have side effects in expressions which construct zero-length bytestrings.

### References
_Are there any links users can visit to find out more?_

## References
- https://github.com/vyperlang/vyper/security/advisories/GHSA-qhr6-mgqr-mchm
- https://nvd.nist.gov/vuln/detail/CVE-2025-47285
- https://github.com/vyperlang/vyper/pull/4644
- https://github.com/vyperlang/vyper
- https://github.com/vyperlang/vyper/blob/68b68c4b30c5ef2f312b4674676170b8a6eaa316/vyper/builtins/functions.py#L560-L562
- https://pypi.org/project/vyper
- https://github.com/advisories/GHSA-qhr6-mgqr-mchm
