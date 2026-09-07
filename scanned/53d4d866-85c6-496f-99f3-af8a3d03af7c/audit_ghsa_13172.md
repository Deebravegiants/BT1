# [M] Vyper's `_abi_decode` input not validated in complex expressions

## Summary
Severity: Medium
Advisory: GHSA-cx2q-hfxr-rj97
CVE: CVE-2023-42460
CWE: CWE-682
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-09-26
Source: https://github.com/advisories/GHSA-cx2q-hfxr-rj97
Type: github-advisory

## Affected
- PyPI: `vyper` — affected >=0.3.4 <0.3.10

## Details
### Impact
`_abi_decode()` does not validate input when it is nested in an expression. the following example gets correctly validated (bounds checked):
```vyper
x: int128 = _abi_decode(slice(msg.data, 4, 32), int128)
```

however, the following example is not bounds checked
```vyper
@external
def abi_decode(x: uint256) -> uint256:
    a: uint256 = convert(_abi_decode(slice(msg.data, 4, 32), (uint8)), uint256) + 1
    return a  # abi_decode(256) returns: 257
```

the issue can be triggered by constructing an example where the output of `_abi_decode` is not internally passed to `make_setter` (an internal codegen routine) or other input validating routine.

### Patches
https://github.com/vyperlang/vyper/pull/3626

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

### References
_Are there any links users can visit to find out more?_

## References
- https://github.com/vyperlang/vyper/security/advisories/GHSA-cx2q-hfxr-rj97
- https://nvd.nist.gov/vuln/detail/CVE-2023-42460
- https://github.com/vyperlang/vyper/pull/3626
- https://github.com/pypa/advisory-database/tree/main/vulns/vyper/PYSEC-2023-191.yaml
- https://github.com/vyperlang/vyper
