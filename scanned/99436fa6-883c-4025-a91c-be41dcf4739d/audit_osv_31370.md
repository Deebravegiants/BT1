# [H] CVE-2025-0343

## Summary
Severity: High
Advisory: CVE-2025-0343
Aliases: GHSA-w8xv-rwgf-4fwh
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-15
Source: https://osv.dev/vulnerability/CVE-2025-0343
Type: osv

## Details
Swift ASN.1 can be caused to crash when parsing certain BER/DER constructions. This crash is caused by a confusion in the ASN.1 library itself which assumes that certain objects can only be provided in either constructed or primitive forms, and will trigger a preconditionFailure if that constraint isn't met.

Importantly, these constraints are actually required to be true in DER, but that correctness wasn't enforced on the early node parser side so it was incorrect to rely on it later on in decoding, which is what the library did.

These crashes can be triggered when parsing any DER/BER format object. There is no memory-safety issue here: the crash is a graceful one from the Swift runtime. The impact of this is that it can be used as a denial-of-service vector when parsing BER/DER data from unknown sources, e.g. when parsing TLS certificates.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/0xxx/CVE-2025-0343.json
- https://github.com/apple/swift-asn1/security/advisories/GHSA-w8xv-rwgf-4fwh
- https://nvd.nist.gov/vuln/detail/CVE-2025-0343
