# [H] pyasn1: Uncontrolled resource consumption when converting decoded REAL values

## Summary
Severity: High
Advisory: GHSA-hm4w-wwcw-mr6r
CVE: CVE-2026-59886
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-hm4w-wwcw-mr6r
Type: github-advisory

## Affected
- PyPI: `pyasn1` — affected >=0 <0.6.4

## Details
### Impact
The univ.Real type converted its (mantissa, base, exponent) value to a Python float using exact big-integer exponentiation. A BER/CER/DER-encoded REAL value only a few bytes long can carry a very large exponent, causing this computation to attempt to materialize an astronomically large integer.

Any operation that triggers float conversion on such a decoded value — prettyPrint(), str(), comparison, arithmetic, or an explicit float() call — consumes excessive CPU and memory, hanging the process. Applications that decode untrusted ASN.1 data and then print, log, or compare the decoded objects are vulnerable to denial of service. Decoding alone does not trigger the issue.

### Affected components
- pyasn1.type.univ.Real — float conversion (__float__() and everything built on it: prettyPrint(), str(), comparisons, arithmetic, int())
- Reachable through the pyasn1.codec.ber, cer, and der decoders, which produce Real objects from untrusted input; also via directly constructed Real values

The encoders and the native codec are not affected. Applications that never handle ASN.1 REAL values are not affected.

### Patches
Fixed in pyasn1 0.6.4. Binary (base-2) values are now converted with math.ldexp(), and decimal (base-10) values with exponents beyond float range raise OverflowError without constructing huge intermediate integers. Existing behavior is preserved: out-of-range values raise OverflowError and prettyPrint() renders them as <overflow>.

### Workarounds
Avoid converting, printing, or comparing decoded Real objects from untrusted sources; inspect the raw (mantissa, base, exponent) tuple instead.

## References
- https://github.com/pyasn1/pyasn1/security/advisories/GHSA-hm4w-wwcw-mr6r
- https://nvd.nist.gov/vuln/detail/CVE-2026-59886
- https://github.com/pyasn1/pyasn1/commit/e60c691cb91addb8fcefa2f537e85ede6fb1e886
- https://github.com/pyasn1/pyasn1
- https://github.com/pyasn1/pyasn1/releases/tag/v0.6.4
