# [H] pyasn1: Quadratic complexity in OBJECT IDENTIFIER and RELATIVE-OID processing allows denial of service

## Summary
Severity: High
Advisory: GHSA-8ppf-4f7h-5ppj
CVE: CVE-2026-59885
CWE: CWE-400, CWE-407
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-8ppf-4f7h-5ppj
Type: github-advisory

## Affected
- PyPI: `pyasn1` — affected >=0 <0.6.4

## Details
### Impact
The BER/CER/DER decoders process OBJECT IDENTIFIER and RELATIVE-OID values in quadratic time relative to the number of arcs. A small crafted payload (tens of kilobytes) containing an OID with many arcs consumes seconds of CPU per decode() call, allowing denial of service in any application that decodes untrusted ASN.1 data (certificates, LDAP, SNMP, Kerberos, etc.). The corresponding encoders have the same quadratic behavior, reachable when an application re-encodes previously decoded attacker-supplied values.

The arc-size limit introduced for CVE-2026-23490 bounds the byte length of an individual arc but not the number of arcs, so it does not mitigate this issue.

### Affected components
ObjectIdentifierPayloadDecoder and RelativeOIDPayloadDecoder in pyasn1/codec/ber/decoder.py; ObjectIdentifierEncoder and RelativeOIDEncoder in pyasn1/codec/ber/encoder.py. The CER and DER codecs inherit these and are equally affected.

### Patches
Fixed in pyasn1 0.6.4: arc accumulation in both decoders and encoders now runs in linear time.

### Workarounds
Limit the size of untrusted ASN.1 input before decoding.

## References
- https://github.com/pyasn1/pyasn1/security/advisories/GHSA-8ppf-4f7h-5ppj
- https://nvd.nist.gov/vuln/detail/CVE-2026-59885
- https://github.com/pyasn1/pyasn1/commit/45bdb19eb7df4b3780fe9c912c63e99bffc39dd9
- https://github.com/pyasn1/pyasn1
- https://github.com/pyasn1/pyasn1/releases/tag/v0.6.4
