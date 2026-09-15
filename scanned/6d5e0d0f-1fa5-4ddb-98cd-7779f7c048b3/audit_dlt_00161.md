# [H] external calls are not clamped in certain complex expressions

## Summary
Severity: High
Chain: Vyper
Component: vyperlang/vyper
CVE: CVE-2022-24845
Published: 2022-04-13
Source: https://github.com/vyperlang/vyper/security/advisories/GHSA-j2x6-9323-fp7h
Type: github-advisory

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
