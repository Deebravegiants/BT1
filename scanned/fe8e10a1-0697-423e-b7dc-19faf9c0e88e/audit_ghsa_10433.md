# [H] ONNX: Malicious ONNX models can crash servers by exploiting unprotected object settings.

## Summary
Severity: High
Advisory: GHSA-538c-55jv-c5g9
CVE: CVE-2026-34445
CWE: CWE-20, CWE-400, CWE-915
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-538c-55jv-c5g9
Type: github-advisory

## Affected
- PyPI: `onnx` — affected >=0 <1.21.0

## Details
### Summary
The ExternalDataInfo class in ONNX was using Python’s setattr() function to load metadata (like file paths or data lengths) directly from an ONNX model file. The problem? It didn’t check if the "keys" in the file were valid. Because it blindly trusted the file, an attacker could craft a malicious model that overwrites internal object properties.

### Why its Dangerous
**Instant Crash DoS**: An attacker can set the length property to a massive number like 9 petabytes. When the system tries to load the model, it attempts to allocate all that RAM at once, causing the server to crash or freeze Out of Memory.

**Access Bypass**: By setting a negative offset -1, an attacker can trick the system into reading parts of a file it wasn't supposed to touch.

**Object Corruption**: Attackers can even inject "dunder" attributes like __class__ to change the object's type entirely, which could lead to more complex exploits.

**Fixed**: https://github.com/onnx/onnx/pull/7751 object state corruption and DoS via ExternalDataInfo attribute injection

## References
- https://github.com/onnx/onnx/security/advisories/GHSA-538c-55jv-c5g9
- https://nvd.nist.gov/vuln/detail/CVE-2026-34445
- https://github.com/onnx/onnx/pull/7751
- https://github.com/onnx/onnx/commit/e30c6935d67cc3eca2fa284e37248e7c0036c46b
- https://github.com/onnx/onnx
