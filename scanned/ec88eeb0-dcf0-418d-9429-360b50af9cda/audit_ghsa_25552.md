# [H] Integer bounds error in Vyper

## Summary
Severity: High
Advisory: GHSA-j2x6-9323-fp7h
CVE: CVE-2022-24845
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-j2x6-9323-fp7h
Type: github-advisory

## Affected
- PyPI: `vyper` — affected >=0 <0.3.2

## Details
### Impact
in the following code, the return of `<iface>.returns_int128()` is not validated to fall within the bounds of `int128`. as of v0.3.0, `<iface>.returns_int128()` is validated in simple expressions, but not complex expressions.
```vyper
interface iface:
    def returns_int128() -> int128: view
    def returns_Bytes33() -> Bytes[33]: view

x: iface
 
@external
def call_out():
    x: int128 = self.x.returns_int128()  # affected, <0.3.0
    y: uint256 = convert(self.x.returns_int128(), uint256)  # affected, <0.3.2
    z: Bytes[33] = concat(self.x.returns_Bytes33(), b"")  # affected >= 0.3.0, <0.3.2
```

### Patches
0.3.2 (as of https://github.com/vyperlang/vyper/commit/049dbdc647b2ce838fae7c188e6bb09cf16e470b)

### Workarounds
Break up operations involving external calls into multiple statements. For instance, instead of the example above, use
```
x: int128 = self.x.returns_int128()
y: uint256 = convert(x, uint256)
```

## References
- https://github.com/vyperlang/vyper/security/advisories/GHSA-j2x6-9323-fp7h
- https://nvd.nist.gov/vuln/detail/CVE-2022-24845
- https://github.com/vyperlang/vyper/commit/049dbdc647b2ce838fae7c188e6bb09cf16e470b
- https://github.com/pypa/advisory-database/tree/main/vulns/vyper/PYSEC-2022-198.yaml
- https://github.com/vyperlang/vyper
