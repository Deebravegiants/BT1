# [H] vyper vulnerable to storage allocator overflow

## Summary
Severity: High
Advisory: GHSA-mgv8-gggw-mrg6
CVE: CVE-2023-30837
CWE: CWE-789
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-05-05
Source: https://github.com/advisories/GHSA-mgv8-gggw-mrg6
Type: github-advisory

## Affected
- PyPI: `vyper` — affected >=0 <0.3.8

## Details
### Impact
The storage allocator does not guard against allocation overflows. This can result in vulnerabilities like the following:
```vyper
owner: public(address)
take_up_some_space: public(uint256[10])
buffer: public(uint256[max_value(uint256)])

@external
def initialize():
    self.owner = msg.sender

@external
def foo(idx: uint256, data: uint256):
    self.buffer[idx] = data
```
Per @toonvanhove, "An attacker can overwrite the owner variable by calling this contract with calldata: `0x04bc52f8 fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff5 ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff` (spaces inserted for readability)
`0x04bc52f8` is the selector for `foo(uint256, uint256)`, and the last argument `fff...fff` is the new value for the owner variable."

### Patches
patched in 0bb7203b584e771b23536ba065a6efda457161bb

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

### References
_Are there any links users can visit to find out more?_

## References
- https://github.com/vyperlang/vyper/security/advisories/GHSA-mgv8-gggw-mrg6
- https://nvd.nist.gov/vuln/detail/CVE-2023-30837
- https://github.com/vyperlang/vyper/commit/0bb7203b584e771b23536ba065a6efda457161bb
- https://github.com/pypa/advisory-database/tree/main/vulns/vyper/PYSEC-2023-76.yaml
- https://github.com/vyperlang/vyper
