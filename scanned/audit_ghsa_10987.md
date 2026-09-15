# [H] cbor2 has a Denial of Service via Uncontrolled Recursion in cbor2.loads

## Summary
Severity: High
Advisory: GHSA-3c37-wwvx-h642
CVE: CVE-2026-26209
CWE: CWE-674
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-3c37-wwvx-h642
Type: github-advisory

## Affected
- PyPI: `cbor2` — affected >=0 <5.9.0

## Details
### Summary

- The `cbor2` library is vulnerable to a Denial of Service (DoS) attack caused by uncontrolled recursion when decoding deeply nested CBOR structures.
- This vulnerability affects both the pure Python implementation and the C extension (`_cbor2`). The C extension correctly uses Python's C-API for recursion protection (`Py_EnterRecursiveCall`), but this mechanism is designed to prevent a stack overflow by raising a `RecursionError`. In some environments, this exception is not caught, thus causing the service process to terminate.
- While the library handles moderate nesting, it lacks a configurable, data-driven depth limit independent of Python's global recursion setting. An attacker can supply a crafted CBOR payload containing thousands of nested arrays (e.g., `0x81`). When `cbor2.loads()` attempts to parse this, it hits the interpreter's recursion limit, causing the call to raise a `RecursionError`.
- By sending a stream of small (<100KB) malicious packets, an attacker can repeatedly crash worker processes faster than they can be restarted, resulting in a complete and sustained Denial of Service.

### Details

- The vulnerability stems from the recursive design of the `CBORDecoder` class, specifically how it decodes nested container types like Arrays and Maps.
- Inside `decode_array` (and similarly `decode_map`), the decoder iterates through the number of elements specified in the CBOR header. For each element, it calls `self.decode()` again to parse the nested item. This recursive call lacks a depth-tracking mechanism.
- Vulnerable Code Locations:
  - `cbor2/decoder.py` (Pure Python implementation)
  - `source/decoder.c` (C extension implementation)
- Execution Flow:
  1. The `cbor2.loads()` function initializes a `CBORDecoder` and calls its `decode()` method.
  2. The `decode()` method reads the initial byte and dispatches control to a specific handler based on the major type. For an Array (Major Type 4), it calls `decode_array`.
  3. `decode_array` loops and calls `self.decode()` for each item, leading to deep recursion when parsing a payload like `[...[...[1]...]...]`.

### PoC

```
import cbor2

DEPTH = 1000

payload = b'\x81' * DEPTH + b'\x01'
print(f"[*] Payload size: {len(payload) / 1024:.2f} KB")
print("[*] Triggering decoder...")

try:
    cbor2.loads(payload)
    print("[+] Parsed successfully (Not Vulnerable)")
except RecursionError:
    print("\n[!] VULNERABLE: RecursionError triggered!")
except Exception as e:
    print(f"\n[-] Unexpected Error: {type(e).__name__}: {e}")
```

### Impact

- Scope: This vulnerability affects any application using `cbor2` to parse untrusted data. Common use cases include IoT data processing, WebAuthn (FIDO2) authentication flows, and inter-service communication over COSE (CBOR Object Signing and Encryption).
- Attack Vector: A remote, unauthenticated attacker can achieve a full Denial of Service with a highly efficient, low-bandwidth attack. A payload under 100KB is sufficient to reliably terminate a Python worker process.

### Credit

This issue was discovered by Kevin Tu of TMIR at ByteDance. The patch was developed by @agronholm.

## References
- https://github.com/agronholm/cbor2/security/advisories/GHSA-3c37-wwvx-h642
- https://nvd.nist.gov/vuln/detail/CVE-2026-26209
- https://github.com/agronholm/cbor2/pull/275
- https://github.com/agronholm/cbor2/commit/e61a5f365ba610d5907a0ae1bc72769bba34294b
- https://github.com/agronholm/cbor2
- https://github.com/agronholm/cbor2/releases/tag/5.9.0
