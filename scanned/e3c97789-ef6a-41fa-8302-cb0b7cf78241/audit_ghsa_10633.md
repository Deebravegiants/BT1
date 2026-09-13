# [M] openssl-encrypt's unverified key bundle from_dict() + to_identity() path allows encryption to attacker keys

## Summary
Severity: Medium
Advisory: GHSA-8h88-gxp3-j7pg
CWE: CWE-347
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-8h88-gxp3-j7pg
Type: github-advisory

## Affected
- PyPI: `openssl-encrypt` — affected >=0 <1.4.0

## Details
### Summary

The `PublicKeyBundle.from_dict()` method in `openssl_encrypt/modules/key_bundle.py` at **lines 329-361** creates bundles from untrusted data without verifying the signature. The docstring warns to call `verify_signature()` after creation, but the `to_identity()` method (line 363-391) can convert an unverified bundle directly to an `Identity` object.

### Affected Code

```python
@classmethod
def from_dict(cls, data: Dict) -> "PublicKeyBundle":
    """
    SECURITY: Does NOT verify signature. Call verify_signature() after creation.
    """
    # Creates bundle without verification
```

### Impact

If `from_dict()` followed by `to_identity()` is called without an intervening `verify_signature()` call, encryption could be performed against an attacker's public key, leaking secrets. While `key_resolver.py` (lines 146-147) does verify before use, the unguarded API path remains directly callable.

### Recommended Fix

- Add a `verified` flag to `PublicKeyBundle` that must be set before `to_identity()` can be called
- Or have `to_identity()` automatically call `verify_signature()` and raise on failure
- Or make `from_dict()` require verification as part of construction

### Fix

Fixed in commit `f4a1ba6` on branch `releases/1.4.x` — from_dict() now verifies self_signature by default (verify=True parameter); raises ValueError on verification failure.

## References
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-8h88-gxp3-j7pg
- https://github.com/jahlives/openssl_encrypt/commit/f4a1ba660063cd9e17883829e5272a248525a16b
- https://github.com/jahlives/openssl_encrypt
